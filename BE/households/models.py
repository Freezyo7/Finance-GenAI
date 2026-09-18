import uuid
import secrets
from django.conf import settings
from django.db import models
from django.utils import timezone
from datetime import timedelta

# Create your models here.


class Household(models.Model):

    class Type(models.TextChoices):
        PERSONAL = "PERSONAL", "Personal"
        FAMILY = "FAMILY", "Family"

    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable = False)
    name = models.CharField(max_length=100)
    type = models.CharField(
        max_length=10,
        choices=Type.choices,
        default=Type.PERSONAL,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_households",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Household"
        verbose_name_plural = "Households"

    def __str__(self) -> str:
        return f"{self.name} ({self.type})"


class HouseholdMember(models.Model):

    class Role(models.TextChoices):
        OWNER = "OWNER", "Owner"
        ADMIN = "ADMIN", "Admin"
        MEMBER = "MEMBER", "Member"
        VIEWER = "VIEWER", "Viewer"

    class Relationship(models.TextChoices):
        SELF = "SELF", "Self"
        FATHER = "FATHER", "Father"
        MOTHER = "MOTHER", "Mother"
        SPOUSE = "SPOUSE", "Spouse"
        CHILD = "CHILD", "Child"
        OTHER = "OTHER", "Other"

    class Status(models.TextChoices):
        INVITED = "INVITED", "Invited"
        ACTIVE = "ACTIVE", "Active"
        SUSPENDED = "SUSPENDED", "Suspended"
        REMOVED = "REMOVED", "Removed"
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    household = models.ForeignKey(
        Household, on_delete=models.CASCADE, related_name="members"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="household_membership" 
    )
    role = models.CharField(
        max_length=10, choices=Role.choices, default=Role.MEMBER
    )
    relationship = models.CharField(
        max_length=15, choices=Relationship.choices,
        default=Relationship.OTHER
    )
    status = models.CharField(
        max_length = 15, choices=Status.choices, default=Status.ACTIVE
    )
    joined_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["joined_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["household", "user"],
                name="unique_household_user_membership"
            )
        ]
        
    def __str__(self) -> str:
        return f"{self.user.email} - {self.role} ({self.relationship}) in {self.household.name}"


def default_invitation_expiry():
    return timezone.now() + timedelta(days=7)

class HouseholdInvitaion(models.Model):

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        ACCEPTED = "ACCEPTED", "Accepted"
        EXPIRED = "EXPIRED", "Expired"
        REVOKED = "REVOKED", "Revoked"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    household = models.ForeignKey(
        Household,
        on_delete=models.CASCADE,
        related_name="invitaions"
    )
    
    email = models.EmailField()
    role = models.CharField(
        max_length=10,
        choices=HouseholdMember.Role.choices,
        default=HouseholdMember.Role.MEMBER,
    )
    relationship = models.CharField(
        max_length=15,
        choices=HouseholdMember.Relationship.choices,
        default=HouseholdMember.Relationship.OTHER,
    )
    token = models.CharField(max_length=64, unique=True, default=secrets.token_urlsafe)
    status = models.CharField(
        max_length=15, choices=Status.choices, default=Status.PENDING
    )
    expires_at = models.DateTimeField(default=default_invitation_expiry)
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_invitations"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Household Invitation"
        verbose_name_plural = "Household Invitations"
    def is_valid(self) -> bool:
        return self.status == self.Status.PENDING and self.expires_at > timezone.now()
    def __str__(self) -> str:
        return f"Invite {self.email} -> {self.household.name} ({self.status})"
