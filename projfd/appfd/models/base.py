#-*- coding: utf-8 -*-
from django.contrib.gis.db.models import DateTimeField, Model

class Base(Model):

    created = DateTimeField(auto_now_add=True, null=True)
    modified = DateTimeField(auto_now=True, null=True)

    class Meta:
        abstract = True

    def __str__(self):
        try:
            for propname in ["name", "key", "token", "text"]:
                if hasattr(self, propname):
                    text = getattr(self, propname).encode("utf-8")
                    if len(text) > 20:
                        return text[:20] + "..."
                    else:
                        return text
            else:
                return str(self.id)
        except:
            return str(self.id)

    def update(self, d):
        save = False
        for k,v in d.iteritems():
            if getattr(self, k) != v:
                save = True
                setattr(self,k,v)
        if save:
            self.save()
