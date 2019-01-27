from .db import Base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.types import Time, Boolean
from sqlalchemy.orm import relationship
from prettytable import PrettyTable


class Questionnaire(Base):
    NULL_EXPIRATION_STR = 'day end'
    DEFAULT_RETENTION = 2
    __tablename__ = 'questionnaire'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    name = Column(String(256), unique=True, nullable=False)
    title = Column(String(256), nullable=False)
    expiration = Column(Time(), nullable=True)
    retention = Column(Integer(), default=DEFAULT_RETENTION, nullable=False)
    active = Column(Boolean(), default=True, nullable=False)
    subscriptions = relationship(
        'Subscription',
        back_populates='questionnaire',
        cascade="all, delete-orphan"
    )

    questions = relationship(
        'Question',
        back_populates='questionnaire',
        cascade="all, delete-orphan"
    )
    schedule = relationship(
        'Schedule',
        back_populates='questionnaire',
        cascade="all, delete-orphan"
    )

    @staticmethod
    def create_pretty_table():
        t = PrettyTable()
        t.field_names = [
            'name',
            'title',
            'questions',
            'expiration',
            'retention(days)',
            'schedule',
            'subs',
            'active'
        ]
        return t

    def to_pretty_table_row(self):
        exp = self.expiration
        if exp is None:
            exp = self.NULL_EXPIRATION_STR
        return [
            self.name,
            self.title,
            len(self.questions),
            exp,
            self.retention,
            len(self.schedule),
            len(
                [
                    s for s in self.subscriptions
                    if s.active
                    and s.subscriber.active
                    and not s.subscriber.archived
                ]
            ),
            self.active
        ]

    @staticmethod
    def to_pretty_table(quests):
        t = Questionnaire.create_pretty_table()
        for q in quests:
            t.add_row(q.to_pretty_table_row())
        return t


class Schedule(Base):
    __tablename__ = 'schedule'
    id = Column(
        Integer(),
        primary_key=True
    )
    start = Column(
        Integer(),
        nullable=False
    )
    end = Column(
        Integer(),
        nullable=False
    )
    time = Column(
        Time(),
        nullable=False
    )
    questionnaire_id = Column(
        Integer(),
        ForeignKey(
            'questionnaire.id',
            ondelete='CASCADE'
        ),
        nullable=False
    )
    questionnaire = relationship(
        'Questionnaire',
        uselist=False,
        back_populates='schedule'
    )

    @staticmethod
    def create_pretty_table():
        t = PrettyTable()
        t.field_names = [
            "start",
            "end",
            "time"
        ]
        return t

    def to_pretty_table_row(self):
        return [
            self.start,
            self.end,
            self.time
        ]

    @staticmethod
    def to_pretty_table(rows):
        t = Schedule.create_pretty_table()
        for r in rows:
            t.add_row(r.to_pretty_table_row())
        return t


class Question(Base):
    __tablename__ = 'question'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    questionnaire_id = Column(
        Integer(),
        ForeignKey(
            'questionnaire.id',
            ondelete='CASCADE'
        ),
        nullable=True
    )
    text = Column(String(256), nullable=False)

    questionnaire = relationship(
        'Questionnaire',
        uselist=False
    )

    answers = relationship(
        'Answer',
        back_populates='question'
    )
