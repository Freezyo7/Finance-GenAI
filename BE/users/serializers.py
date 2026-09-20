from typing import Required
from dataclasses import Field
from dataclasses import field
from typing import Any
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken 

from households.models import Household, HouseholdMember

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "created_at"]
        read_only_fields = ["id", "created_at"]

class RegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    tokens = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "password", "first_name", "last_name", "tokens"]
        read_only_fields = ["id", "tokens"]

    def get_tokens(self, user:Any) -> dict[str, str]:
        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
    
    def create(self, validated_data: dict[str, Any]) -> Any:
        with transaction.atomic():
            user = User.objects.create_user(
                email=validated_data["email"],
                password=validated_data["password"],
                first_name=validated_data.get("first_name", ""),
                last_name=validated_data.get("last_name", ""),

            )

            personal_household = Household.objects.create(
                name=f"{user.first_name or user.email.split('@')[0]}'s Workspace",
                type=Household.Type.PERSONAL,
                created_by=user,
            )

            HouseholdMember.objects.create(
                household=personal_household,
                user=user,
                role=HouseholdMember.Role.OWNER,
                relationship=HouseholdMember.Relationship.SELF,
                status=HouseholdMember.Status.ACTIVE,
            )

            return user

class ChangePasswordSerializer(serializers.Serializer):

    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
