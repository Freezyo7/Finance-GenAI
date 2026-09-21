from typing import Any
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers
from users.serializers import UserSerializer
from .models import Household, HouseholdInvitation, HouseholdMember

class HouseholdMemberSerializer(serializers.ModelSerializer):

    user = UserSerializer(read_only=True)

    class Meta:
        model = HouseholdMember
        fields = [
            "id",
            "user",
            "role",
            "relationship",
            "status",
            "joined_at",
        ]
        read_only_fields = ["id", "user", "joined_at"]

class HouseholdSerializer(serializers.ModelSerializer):

    members_count = serializers.IntegerField(
        source="members.count", read_only=True
    )

    class Meta:
        model = Household
        fields = [
            "id",
            "name",
            "type",
            "created_by",
            "members_count",
            "created_at",
        ]
        read_only_fields = ["id", "created_by", "created_at"]

    def create(self, validated_data: dict[str, Any]) -> Household:
        user = self.context["request"].user
        with transaction.atomic():

            household = Household.objects.create(
                created_by=user, **validated_data
            )

            HouseholdMember.objects.create(
                household=household,
                user=user,
                role=HouseholdMember.Role.OWNER,
                relationship=HouseholdMember.Relationship.SELF,
                status=HouseholdMember.Status.ACTIVE,
            )

            return household