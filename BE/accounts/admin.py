from django.contrib import admin
from .models import FinancialAccount, AccountMember

admin.site.register(FinancialAccount)
admin.site.register(AccountMember)
