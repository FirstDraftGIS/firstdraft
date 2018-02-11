from django.contrib import admin
from appfd.models import Basemap, Order, Place, TeamMember

# Register your models here.
admin.site.register(Basemap)
admin.site.register(Order)
admin.site.register(Place)
admin.site.register(TeamMember)
