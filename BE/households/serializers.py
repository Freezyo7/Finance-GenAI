from rest_framework import status
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


class HouseholdInvitationSerializer(serializers.ModelSerializer):

    invited_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = HouseholdInvitation
        fields = [
            "id",
            "household",
            "email",
            "role",
            "relationship",
            "token",
            "status",
            "expires_at",
            "invited_by",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "household",
            "token",
            "status",
            "expires_at",
            "invited_by",
            "created_at",
        ]

    def create(self, validated_data:dict[str, Any]) -> HouseholdInvitation:
        user = self.context["request"].user
        household = self.context["household"]

        if HouseholdMember.objects.filter(
            household=household, 
            user__email=validated_data["email"], # the person who is bieng invited.
            status=HouseholdMember.Status.ACTIVE
        ).exists():
            raise serializers.ValidationError("This user is already an active member of this household.")

        return HouseholdInvitation.objects.create(
            household=household,
            invited_by=user,
            **validated_data,
        )

class AcceptInvitationSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)

    def validate_token(self, value:str) -> HouseholdInvitation:
        try:
            invitation = HouseholdInvitation.objects.get(token=value)

        except HouseholdInvitation.DoesNotExists:
            raise serializers.ValidationError("Invalid invitation token.")
        
        if not invitation.is_valid():
            raise serializers.ValidationError("This invitation has expired or already been used.")

        return invitation

    def save(self, **kwargs:Any) -> HouseholdMember:
        invitation: HouseholdInvitation = self.validated_data["token"]
        user = self.context["request"].user

        with transaction.atomic():
            member, created = HouseholdMember.objects.update_or_create(
                household = invitation.household,
                user = user,
                defaults = {
                    "role": invitation.role,
                    "relationship": invitation.relationship,
                    "status": HouseholdMember.Status.ACTIVE,
                },
            )

            invitation.status = HouseholdInvitation.Status.ACCEPTED
            invitation.save()

            return member