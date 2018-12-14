from .db import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship


class Subscriber(Base):
    __tablename__ = 'subscriber'
    id = Column(String(256), primary_key=True)
    name = Column(String(256), unique=True)
    display_name = Column(String(256), nullable=False)
    admin = Column(Boolean(), default=False)
    channel_id = Column(String(256), unique=True)
    tz = Column(String(256), nullable=False)
    active = Column(Boolean(), default=True)

    subscriptions = relationship(
        'Subscription',
        back_populates='subscriber'
    )


class Subscription(Base):
    __tablename__ = 'subscription'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    questionnaire_id = Column(
        Integer(),
        ForeignKey('questionnaire.id'),
        nullable=False
    )
    subscriber_id = Column(
        String(256),
        ForeignKey('subscriber.id'),
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
