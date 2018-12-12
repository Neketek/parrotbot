from .db import Base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.types import Time
from sqlalchemy.orm import relationship


class Questionnaire(Base):
    __tablename__ = 'questionnaire'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    title = Column(String(256), unique=True, nullable=False)
    subscriptions = relationship(
        'Subscription',
        back_populates='questionnaire'
    )

    questions = relationship(
        'Question',
        back_populates='questionnaire'
    )
    schedule = relationship(
        'Schedule',
        back_populates='questionnaire'
    )


class Schedule(Base):
    __tablename__ = 'schedule',
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
        ForeignKey('questionnaire.id'),
        nullable=False
    )
    questionnaire = relationship(
        'Questionnaire',
        uselist=False,
        back_populates='schedule'
    )


class Question(Base):
    __tablename__ = 'question'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    questionnaire_id = Column(
        Integer(),
        ForeignKey('questionnaire.id'),
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
