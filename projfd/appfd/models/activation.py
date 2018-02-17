#-*- coding: utf-8 -*-
from .base import Base
from django.contrib.gis.db.models import BooleanField, CASCADE, CharField, OneToOneField
from django.contrib.auth.models import User

class Activation(Base):
    expired = BooleanField(default=False)
    key = CharField(max_length=200)
    notified_success = BooleanField(default=False)
    used = BooleanField(default=False)
    user = OneToOneField(User, on_delete=CASCADE)