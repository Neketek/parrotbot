from marshmallow import Schema, fields as f, validate as v
from modules.model.sql import Questionnaire, Question, Subscriber


class TemplateSchema(Schema):
    title = f.Str(
        validate=v.Length(
            min=1,
            max=Questionnaire.title.property.columns[0].type.length
        )
    )
    questions = f.List(
        f.Str(
            validate=v.Length(
                min=1,
                max=Question.text.property.columns[0].type.length
            )
        ),
        validate=v.Length(min=1)
    )
    subscribers = f.List(
        f.Str(
            validate=v.Length(
                min=1,
                max=Subscriber.name.property.columns[0].type.length
            )
        ),
        validate=v.Length(min=1)
    )
    schedule = f.List(
        f.List(
            f.Str(),
            validate=v.Length(min=2)
        ),
        validate=v.Length(min=1)
    )
