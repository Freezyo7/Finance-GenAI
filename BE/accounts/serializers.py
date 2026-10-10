from secrets import choice
from typing import Any
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers

from households.models import HouseholdMember
from users.serializers import UserSerializer
from .models import AccountMember, FinancialAccount

User = get_user_model()

class AccountMemberSerializer(serializers.ModelSerializer):

    user = UserSerializer(read_only=True)
    user_email = serializers.EmailField(write_only=True, required=False)

    class Meta:
        model = AccountMember
        fields = [
            "id",
            "account",
            "user",
            "user_email",
            "permisssion",
            "created_at",
        ]

        read_only_fields = ["id", "account", "user", "created_at"]


class FinancialAccountSerializer(serializers.ModelSerializer):
    """Handles viewing, updating, and creating Financial Accounts."""

    members = AccountMemberSerializer(many=True, read_only=True)
    current_user_permission = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = FinancialAccount
        fields = [
            "id",
            "households",
            "name",
            "account_type",
            "intuition",
            "currency",
            "balance",
            "current_user_permission",
            "members",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "household", "created_at", "updated_at"]

    def get_current_user_permission(self, obj: FinancialAccount) -> str | None:

        user = self.context["request"].user
        membership = AccountMember.obj.filter(
            account=obj,
            user=user
        ).first()

        if membership:
            return membership.permission
        
        if HouseholdMember.object.filter(
            household=obj.household, user=user,
            role = HouseholdMember.Role.OWNER
        ).exists():
            return "HOUSEHOLD_OWNER"
        return None

    def create(self, validated_data:dict[str, Any]) -> FinancialAccount:
        user = self.context["request"].user
        household = self.context["household"]

        with transaction.atomic():
            account = FinancialAccount.objects.create(
                household=household,
                **validated_data,
            )

            AccountMember.objects.create(
                account=account,
                user=user,
                permission=AccountMember.Permission.OWNER
            )

            return account

class ShareAccountSerializer(serializers.Serializer):
    """Allows an account OWNER to grant account access to another household member."""

    email = serializers.EmailField(required=True)
    permission = serializers.CharField(
        choices=[AccountMember.Permission.EDITOR,
        AccountMember.Permission.VIEWER],
        default=AccountMember.Permission.VIEWER
    )

    def validate_email(self, value:str) -> Any:
        account = self.context["account"]

        try:
            target_user = User.object.get(email=value)

        except User.DoesNotExist:
            raise serializers.ValidationError("No user found with this email.")

        if not HouseholdMember.objects.filter(
            household=account.household,
            user=target_user,
            status=HouseholdMember.Status.ACTIVE,
        ).exists():
            raise serializers.ValidationError("This user is not an active member of thi household.")

        return target_user

    def save(self, **kwargs: Any) -> AccountMember:
        target_user = self.validated_data["email"]
        permission = self.validated_data["permission"]
        account = self.context["account"]

        member, created = AccountMember.objects.update_or_create(
            account=account,
            user=target_user,
            default={"permission":permission},
        )

        return member