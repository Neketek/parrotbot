from modules.controller.create.questionnaire import schema as cschema
from marshmallow import Schema, validates_schema


class TemplateSchema(Schema):
    name = cschema.NameField(required=True)
    title = cschema.TitleField(required=False)
    expiration = cschema.ExpirationField(required=False)
    retention = cschema.RetentionField(required=False)
    subscribers = cschema.SubscribersField(required=False)
    schedule = cschema.ScheduleField(required=False)

    @validates_schema
    def __validate_schema(self, data):
        cschema.validate_schedule_days_intersection(data.get('schedule'))
