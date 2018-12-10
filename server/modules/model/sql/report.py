from .db import Base
from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.types import DateTime
from sqlalchemy.orm import relationship


class Report(Base):
    __tablename__ = 'report'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    created = Column(DateTime(), nullable=False)
    completed = Column(DateTime(), nullable=True)
    subscription_id = Column(
        Integer(),
        ForeignKey('subscription.id'),
        nullable=False
    )
    subsciption = relationship(
        "Subscription",
        back_populates='answers',
        uselist=False
    )
    answers = relationship(
        "Answer",
        back_populates='report'
    )


class Answer(Base):
    __tablename__ = 'answer',
    id = Column(Integer(), primary_key=True)
    question_id = Column(Integer(), ForeignKey('question.id'), nullable=False)
    report_id = Column(Integer(), ForeignKey('report.id'), nullable=False)
    text = Column(String(512), nullable=False)
    report = relationship(
        'Report',
        back_populates='answers',
        uselist=False
    )
    question = relationship(
        'Question',
        back_populates='answers',
        uselist=False
    )
