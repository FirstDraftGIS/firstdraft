#-*- coding: utf-8 -*-
from base import Base
from django.contrib.gis.db.models import *
from django.contrib.auth.models import User

class Alert(Base):
    colors = (("danger", "danger"),("info", "info"),("success", "success"),("warning","warning"))
    color = CharField(choices=colors, max_length=200)
    permanent = BooleanField()
    text = CharField(max_length=200)
    user = OneToOneField(User, blank=True, null=True)
    def __str__(self):
        return self.text
