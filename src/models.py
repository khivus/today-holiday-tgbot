# from tortoise import Model, fields


# class User(Model):
#     user_id = fields.IntField(pk=True)
#     uses = fields.IntField(default=0)

#     settings: fields.ReverseRelation['Settings']


# class Settings(Model):
#     time = fields.TextField(null=True)
#     enabled = fields.BooleanField(default=False)
#     only_rus = fields.BooleanField(default=False)
#     name_day = fields.BooleanField(default=True)
#     day_of_remembrance = fields.BooleanField(default=True)

#     user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
#         model_name='models.User',
#         related_name='settings'
#     )
