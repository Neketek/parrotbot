from marshmallow import \
    Schema,\
    fields as f,\
    validate as v,\
    validates_schema,\
    ValidationError
from modules.model.sql import Questionnaire, Question, Subscriber
from datetime import datetime


def duplication_validator(value):
    try:
        v = value[0]
    except IndexError:
        return
    if isinstance(v, dict):
        value = [tuple(v.items()) for v in value]
    if len(set(value)) != len(value):
        raise ValidationError("Duplicates found")


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


def validate_schedule_days_intersection(schedule):
    days = [False]*7
    for sch in schedule:
        start = sch['start']
        end = sch['end']
        for i in range(start-1, end):
            if days[i]:
                raise ValidationError(
                    'Day intervals intersection.',
                    'schedule'
                )
            else:
                days[i] = True


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


def StrField(prop, *args, **kwargs):
    return f.Str(
        validate=v.Length(
            min=1,
            max=prop.property.columns[0].type.length
        ),
        *args,
        **kwargs,
    )


def SubscribersField(*args, **kwargs):
    return f.List(
        StrField(Subscriber.name),
        validate=(v.Length(min=1), duplication_validator, ),
        *args,
        **kwargs
    )


def ScheduleField(*args, **kwargs):
    return f.Nested(
        ScheduleSchema,
        many=True,
        validate=duplication_validator,
        *args,
        **kwargs
    )


def QuestionsField(*args, **kwargs):
    return f.List(
        StrField(Question.text),
        validate=(v.Length(min=1), duplication_validator, ),
        *args,
        **kwargs
    )


def RetentionField(*args, **kwargs):
    return f.Integer(validate=gt_validator(1))


def ExpirationField(*args, **kwargs):
    return f.Str(validate=time_str_validator, *args, **kwargs)


def TitleField(*args, **kwargs):
    return StrField(Questionnaire.name, *args, **kwargs)


def NameField(*args, **kwargs):
    return StrField(Questionnaire.title, *args, **kwargs)


class TemplateSchema(Schema):
    name = NameField(required=True)
    title = TitleField(required=True)
    expiration = ExpirationField()
    retention = RetentionField()
    questions = QuestionsField(required=True)
    subscribers = SubscribersField(required=True)
    schedule = ScheduleField(required=False)

    @validates_schema
    def __validate_schema(self, data):
        validate_schedule_days_intersection(data.get('schedule'))
