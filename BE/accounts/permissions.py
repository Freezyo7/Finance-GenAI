from django.shortcuts import resolve_url
from typing import Final
from typing import Any
from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import APIView

from households.models import HouseholdMember
from .models import AccountMember, FinancialAccount

class HasAccountAccess(permissions.BasePermission):

    def has_object_permission(self, request:Request, view:APIView, obj:Any) -> bool:
        if isinstance (obj, FinancialAccount):
            account = obj
        else:
            account = getattr(obj, "account", None)

        if not account:
            return False

        if HouseholdMember.objects.filter(
            household=account.household,
            user=request.user,
            role=HouseholdMember.Role.OWNER,
            status=HouseholdMember.Status.ACTIVE,
        ).exists():
            return True

        return AccountMember.objects.filter(
            account=account,
            user=request.user,
        ).exists()

class CanEditAccount(permissions.BasePermission):

    def has_object_permission(self, request: Request, view: APIView, obj: Any) -> bool:
        
        if isinstance (obj, FinancialAccount):
            account = obj

        else:
            account = getattr(obj, "account", None)

        if not account:
            return False

        if HouseholdMember.objects.filter(
            household=account.household,
            user=request.user,
            role=HouseholdMember.Role.OWNER,
            status=HouseholdMember.Status.ACTIVE,
        ).exists():
            return True

        return AccountMember.objects.filter(
            account=account,
            user=request.user,
            permission__in=[AccountMember.Permission.OWNER, AccountMember.Permission.EDITOR],
        ).exists()

class IsAccountOwner(permissions.BasePermission):

    def has_object_permission(self, request:Request, view:APIView, obj:Any) -> bool:

        if isinstance(obj, FinancialAccount):
            account = obj
        
        else:
            account = getattr(obj, "account", None)

        if not account:
            return False
        
        return AccountMember.objects.filter(
            account=account,
            user=request.user,
            permission=AccountMember.Permission.OWNER
        ).exists()
        