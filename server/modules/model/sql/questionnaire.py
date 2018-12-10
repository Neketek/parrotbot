from .db import Base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship


class Questionnaire(Base):
    __tablename__ = 'questionnaire'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    title = Column(String(256), unique=True, nullable=False)

    subscriptions = relationship(
        'Subsciption',
        back_populates='questionnaire'
    )

    questions = relationship(
        'Question',
        back_populates='questionnaire'
    )

    answers = relationship(
        'Answers',
        back_populates='question'
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
