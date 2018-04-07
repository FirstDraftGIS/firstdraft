from django.contrib import admin
from appfd.models import Basemap, Order, Place, TeamMember

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    pass
    
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    pass
