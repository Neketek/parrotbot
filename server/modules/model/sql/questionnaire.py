from .db import Base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship


class Questionnaire(Base):
    __tablename__ = 'questionnaire'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    title = Column(String(256), unique=True, nullable=False)

    @staticmethod
    def from_json(json):
        e = Questionnaire()
        try:
            e.title = json['title']
            e.questions = []
            for q in json['questions']:
                e.questions.append(Question(text=q))
            return e
        except KeyError:
            raise ValueError('Invalid json data!')

    def __repr__(self):
        repr = 'Title:{0}\n'.format(self.title)
        repr += 'Questions:\n'
        n = 1
        for q in self.questions:
            repr += '  {0}) {1}\n'.format(n, q.text)
            n += 1
        return repr

    subscriptions = relationship(
        'Subscription',
        back_populates='questionnaire'
    )

    questions = relationship(
        'Question',
        back_populates='questionnaire'
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
