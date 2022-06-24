from datetime import datetime
from email.policy import default
from enum import unique
import peewee
from .database import db

class User(peewee.Model):
    username = peewee.CharField(unique= True)
    email = peewee.CharField(unique=True, index=True)
    hashed_password = peewee.CharField()
    is_active = peewee.BooleanField(default=True)
    class Meta:
        database = db

class Item(peewee.Model):
    title = peewee.CharField(index=True)
    description = peewee.CharField(index=True)
    owner = peewee.ForeignKeyField(User, backref="items")

    class Meta:
        database = db

class Token(peewee.Model):
    owner = peewee.ForeignKeyField(User, backref="token")
    token = peewee.CharField(index=True)
    created_at = peewee.DateTimeField(default=datetime.now())

    class Meta:
        database = db