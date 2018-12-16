from marshmallow import \
    Schema,\
    fields as f,\
    validate as v,\
    validates_schema,\
    ValidationError
from modules.model.sql import Questionnaire, Question, Subscriber
from datetime import datetime


def time_str_validator(value):
    try:
        datetime.strptime(value, "%H:%M")
    except ValueError:
        raise ValidationError("Time is not in %H:%M format")


class ScheduleSchema(Schema):
    start = f.Integer(validate=v.Range(min=1, max=7))
    end = f.Integer(validate=v.Range(min=1, max=7))
    time = f.Str(validate=time_str_validator)

    @validates_schema
    def __validate_schema(self, data):
        if data['start'] > data['end']:
            raise ValidationError(
                "start must be less or equal than end",
                "start"
            )


class TemplateSchema(Schema):
    title = f.Str(
        validate=v.Length(
            min=1,
            max=Questionnaire.title.property.columns[0].type.length
        )
    )
    expiration = f.Str(validate=time_str_validator, required=False)
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

    schedule = f.Nested(ScheduleSchema, many=True)

    @validates_schema
    def __validate_schema(self, data):
        schedule = data['schedule']
        duplicated = 0
        for s in schedule:
            for ds in schedule:
                if ds == s:
                    duplicated += 1
                if duplicated > 1:
                    raise ValidationError(
                        'Schedule has duplicates',
                        'schedule'
                    )
            duplicated = 0
        if len(set(data['questions'])) < len(data['questions']):
            raise ValidationError('Questions has duplicated', 'questions')
        if len(set(data['subscribers'])) < len(data['subscribers']):
            raise ValidationError('Subscribers has duplicated', 'subscribers')
