from .db import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from prettytable import PrettyTable


class Subscriber(Base):
    __tablename__ = 'subscriber'
    id = Column(String(256), primary_key=True)
    name = Column(String(256), unique=True)
    display_name = Column(String(256), nullable=False)
    admin = Column(Boolean(), default=False)
    bot_admin = Column(Boolean(), default=False)
    channel_id = Column(String(256), unique=True)
    tz = Column(String(256), nullable=False)
    active = Column(Boolean(), default=True)

    subscriptions = relationship(
        'Subscription',
        back_populates='subscriber'
    )

    @property
    def role(self):
        return "admin" if self.admin else "member"

    @staticmethod
    def create_pretty_table():
        t = PrettyTable()
        t.field_names = [
            "name",
            "display_name",
            "role",
            "bot_admin",
            "tz",
            "active"
        ]
        return t

    def to_pretty_table_row(self):
        return [
            self.name,
            self.display_name,
            self.role,
            self.bot_admin,
            self.tz,
            self.active
        ]

    @staticmethod
    def to_pretty_table(subs):
        t = Subscriber.create_pretty_table()
        for s in subs:
            t.add_row(s.to_pretty_table_row())
        return t


class Subscription(Base):
    __tablename__ = 'subscription'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    questionnaire_id = Column(
        Integer(),
        ForeignKey(
            'questionnaire.id',
            ondelete='CASCADE'
        ),
        nullable=False
    )
    subscriber_id = Column(
        String(256),
        ForeignKey(
            'subscriber.id',
            ondelete='CASCADE'
        ),
        nullable=False
    )
    active = Column(Boolean(), default=True)
    subscriber = relationship(
        'Subscriber',
        uselist=False,
        back_populates='subscriptions'
    )
    questionnaire = relationship(
        'Questionnaire',
        uselist=False,
        back_populates='subscriptions'
    )
    reports = relationship(
        'Report',
        back_populates='subscription'
    )

    @staticmethod
    def create_pretty_table():
        t = PrettyTable()
        t.field_names = [
            'name',
            'display_name',
            'subscriber_active',
            'active'
        ]
        return t

    def to_pretty_table_row(self):
        return [
            self.subscriber.name,
            self.subscriber.display_name,
            self.subscriber.active,
            self.active
        ]

    @staticmethod
    def to_pretty_table(subscrs):
        t = Subscription.create_pretty_table()
        for s in subscrs:
            t.add_row(s.to_pretty_table_row())
        return t
