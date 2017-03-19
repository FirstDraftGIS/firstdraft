# In forms.py...
from appfd.models import Basemap
from django.forms import CharField, FileField, Form, ModelChoiceField, URLField

class BasemapForm(Form):
    basemap = ModelChoiceField(to_field_name="name", queryset=Basemap.objects.all())

class LinkForm(Form):
    data = URLField()

class TextForm(Form):
    data = CharField()

class FileForm(Form):
    data = FileField()
