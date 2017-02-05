import peewee as pw

db = pw.SqliteDatabase("israel-post-bot.db")


class BaseModel(pw.Model):
    class Meta:
        database = db


class Users(BaseModel):
    user_id = pw.PrimaryKeyField()
    chat_id = pw.IntegerField()
    signup_date = pw.DateTimeField()


class Packages(BaseModel):
    user = pw.ForeignKeyField(Users, related_name="packages")
    tracking_id = pw.TextField()
    tracking_text = pw.TextField(default="")
    update_time = pw.DateTimeField()

    class Meta:
        database = db
        primary_key = pw.CompositeKey("user", "tracking_id")


db.connect()
db.create_tables([Users, Packages], safe=True)
db.close()
