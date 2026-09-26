from households import permissions
from households import serializers
from typing import Any
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from .models import Household, HouseholdMember, HouseholdInvitation
from .permissions import IshouseholdAdminOrOwner, IsHouseholdMember
from .serializers import (
    HouseholdSerializer,
    HouseholdMemberSerializer,
    HouseholdInvitationSerializer,
    AcceptInvitationSerializer,
)

# Create your views here.

class HousholdListCreateView(generics.ListCreateAPIView):
    """GET /api/households/ - list all households the user belongs to.
    POST /api/households/ - Create a new Household (Personal or Family) """

    permission_classes = [IsAuthenticated]
    serializer_class = HouseholdSerializer

    def get_queryset(self) -> QuerySet[Household]:
        return Household.objects.filter(
            members__user=self.request.user,
            members__status=HouseholdMember.Status.ACTIVE,
        ).distinct()

class HouseholdDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET/PATCH/DELETE /api/households/<id> - Manage a specific household."""
    query_set = Household.objects.all()
    serializer_class = HouseholdSerializer

    def get_permissions(self) -> list[Any]:
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [IsAuthenticated(), IshouseholdAdminOrOwner()]
        return [IsAuthenticated(), IsHouseholdMember()]

class HouseholdMemberListCreateView(generics.ListAPIView):
    """GET /api/households/<id>/members/ - list all active members in a households """

    permissions_classes = [IsAuthenticated, IsHouseholdMember]
    serializers_class = HouseholdMemberSerializer

    def get_queryset(self) -> QuerySet[HouseholdMember]:
        household_id = self.kwargs["households_id"]
        return HouseholdMember.objects.filter(
            household_id=household_id,
            status=HouseholdMember.Status.ACTIVE,
        ).select_related("user")

    def get_object(self) -> Household:
        household = get_object_or_404(Household, id=self.kwargs["household_id"])
        self.check_object_permissions(self.request, household)
        return household

class HouseholdInvitationListCreateView(generics.ListCreateAPIView):
    """POST /api/household/<id>/invitations/ - Invite a member (Admin/Owner only).
    GET /api/households/<id>/invitations/ - List pending invitations. """

    serializer_class = HouseholdInvitationSerializer
    permissions_classes = [IsAuthenticated, IshouseholdAdminOrOwner]

    def get_household(self) -> Household:
        household = get_object_or_404(
            Household,
            id = self.kwargs["household_id"]
        )
        self.check_object_permissions(self.request, household)
        return household

    def get_queryset(self) -> QuerySet["HouseholdInvitation"]:
        return HouseholdInvitation.objects.filter(
            household_id=self.kwargs["household_id"]
        )

    def get_serializer_context(self) -> dict[str, Any]:
        context = super().get_serializer_context()
        context["household"] = self.get_household()
        return context

class AcceptInvitationView(generics.GenericAPIView):
    """POST /api/invitations/accept/ - Accept an invite token to join a household. """

    permission_classes = [IsAuthenticated]
    serializer_class = AcceptInvitationSerializer

    def post(self, request:Request, *args:Any, **kwargs:Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        member = serializer.save()
        return Response(
            HouseholdMemberSerializer(member).data,
            status=status.HTTP_200_OK,
        )