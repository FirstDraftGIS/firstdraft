# In forms.py...
from appfd.models import Basemap
from django.forms import CharField, FileField, Form, ModelChoiceField, URLField
from timezone_field import TimeZoneFormField

class BasemapForm(Form):
    basemap = ModelChoiceField(to_field_name="name", queryset=Basemap.objects.all())

class LinkForm(Form):
    data = URLField()

class TextForm(Form):
    data = CharField()

class FileForm(Form):
    data = FileField()

class RequestPossibleAdditionsForm(Form):
    name = CharField()

    # not validating whether token is in correct tokens bc that would slow
    # things down too much
    token = CharField() 

class TimezoneForm(Form):
    timezone = TimeZoneFormField()

class TweetForm(Form):
    text = CharField()
