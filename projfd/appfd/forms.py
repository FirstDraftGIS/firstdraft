# In forms.py...
from django.forms import CharField, FileField, Form, URLField

class LinkForm(Form):
    data = URLField()

class TextForm(Form):
    data = CharField()

class FileForm(Form):
    data = FileField()
