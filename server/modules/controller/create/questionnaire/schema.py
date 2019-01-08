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


def gt_validator(lower_bound):
    def validator(value):
        if value < lower_bound:
            raise ValidationError(
                "Value must be greater than {}"
                .format(lower_bound)
            )


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


def StrField(prop):
    return f.Str(
        validate=v.Length(
            min=1,
            max=prop.property.columns[0].type.length
        )
    )


class TemplateSchema(Schema):
    name = StrField(Questionnaire.name)
    title = StrField(Questionnaire.title)
    expiration = f.Str(validate=time_str_validator, required=False)
    retention = f.Integer(validate=gt_validator(1), required=False)
    questions = f.List(
        StrField(Question.text),
        validate=v.Length(min=1)
    )
    subscribers = f.List(
        StrField(Subscriber.name),
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
