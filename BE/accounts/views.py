from households.permissions import IshouseholdAdminOrOwner
from accounts import serializers
from typing import Any
from django.db.models import Q, QuerySet
from django.shortcuts import get_object_or_404

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from households.models import Household, HouseholdMember
from households.permissions import IsHouseholdMember

from .models import AccountMember, FinancialAccount

from .permissions import CanEditAccount, HasAccountAccess, IsAccountOwner

from .serializers import (
    AccountMemberSerializer,
    FinancialAccountSerializer,
    ShareAccountSerializer,
)

# Create your views here.

class FinancialAccountListCreateView(generics.ListCreateAPIView):
    """GET/api/households/<household_id>/accounts/ - List accessible accounts in a household. 
    POST/api/households/<household_id>/accoutns/ - Create a new financial account. """

    serializer_class = FinancialAccountSerializer
    permission_classes = [IsAuthenticated, IsHouseholdMember] 

    def get_household(self) ->Household:
        household = get_object_or_404(
            Household,
            id=self.kwargs["household_id"]
            )
        self.check_object_permissions(self.request, household)
        return household

    def get_queryset(self) -> QuerySet[FinancialAccount]:
        household = self.get_household()
        user = self.request.user

        # 1. If user is Household OWNER, they can see all accounts in the household
        is_household_owner = HouseholdMember.objects.filter(
            household=household,
            user=user,
            role=HouseholdMember.Role.OWNER,
            status=HouseholdMember.Status.ACTIVE,
        ).exists()

        if is_household_owner:
            return FinancialAccount.objects.filter(household=household).prefetch_related("members__user")

        return FinancialAccount.objects.filter(
            household=household,
            members__user=user,
        ).prefetch_related("members__user").distinct()

    def get_serializer_context(self) -> dict[str, Any]:
        context = super().get_serializer_context()
        context["household"] = self.get_household()
        return context

class FinancialAccountDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET/PATCH/DELETE /api/accounts/<id> - View, edit, or delete a specific account."""

    queryset = FinancialAccount.objects.all().prefetch_related("members__user")
    serializer_class = FinancialAccountSerializer

    def get_permissions(self) -> list[Any]:

        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [IsAuthenticated(), IsAccountOwner()]

        return [IsAuthenticated(), HasAccountAccess()]

class ShareAccountView(generics.GenericAPIView):

    serializer_class = ShareAccountSerializer
    permission_classes = [IsAuthenticated, IsAccountOwner]

    def get_account(self) -> FinancialAccount:
        account = get_object_or_404(
            FinancialAccount,
            id=self.kwargs["account_id"]
        )
        self.check_object_permissions(self.request, account)
        return account 

    def get_serializer_context(self) -> dict[str, Any]:
        context = super().get_serializer_context()
        context["account"] = self.get_account()
        return context

    def post(self, request:Request, *args:Any, **kawrgs:Any) -> Response:
        serializer = self.get_serializer_context()
        serializer.is_valid(raise_exception=True)
        member = serializer.save()
        return Response(
            AccountMemberSerializer(member).data,
            status=status.HTTP_200_OK,
        )