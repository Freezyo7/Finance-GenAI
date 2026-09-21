from typing import Any
from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import APIView
from .models import Household, HouseholdMember

class IsHouseholdMember(permissions.BasePermission):

    def has_object_permission(self, request: Request, view: APIView, obj: Any) -> bool:
        if isinstance(obj, Household):
            household = obj  
        else:
            household = getattr(obj, "household", None)

        if not household:
            return False

        return HouseholdMember.objects.filter(
            household=household,
            user=request.user,
            status=HouseholdMember.Status.ACTIVE,
        ).exists()

class IshouseholdAdminOrOwner(permissions.BasePermission):
    def has_object_permission(self, request: Request, view: APIView, obj: Any) -> bool:

        if isinstance(obj, Household):
            household = obj
        else:
            household = getattr(obj, "household", None)

        if not household:
            return False

        return HouseholdMember.objects.filter(
            household=household,
            user=request.user,
            role__in=[HouseholdMember.Role.OWNER, HouseholdMember.Role.ADMIN],
            status=HouseholdMember.Status.ACTIVE,
        ).exists()


class IsHouseholdOwner(permissions.BasePermission):

    def has_object_permission(self, request: Request, view: APIView, obj: Any) -> bool:
        household = obj if isinstance(obj, Household) else getattr(obj, "household", None)
        if not household:
            return False
        return HouseholdMember.objects.filter(
            household=household,
            user=request.user,
            role=HouseholdMember.Role.OWNER,
            status=HouseholdMember.Status.ACTIVE,
        ).exists()