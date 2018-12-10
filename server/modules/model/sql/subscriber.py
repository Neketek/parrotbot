from .db import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship


class Subscriber(Base):
    __tablename__ = 'subscriber'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    name = Column(String(256), unique=True)
    slack_id = Column(String(256), unique=True)
    channel_id = Column(String(256), unique=True)

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
        Integer(),
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
    answers = relationship(
        'Answers',
        back_populates='subscription'
    )
