from django.contrib import admin
from .models import Household, HouseholdMember, HouseholdInvitation

admin.site.register(Household)
admin.site.register(HouseholdMember)
admin.site.register(HouseholdInvitation)
