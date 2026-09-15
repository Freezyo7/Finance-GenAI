import uuid
from decimal import Decimal
from django.conf import settings
from django.db import models
from households.models import Household

# Create your models here.

class FinancialAccount(models.Model):

    class AccountType(models.TextChoices):
        BANK_ACCOUNT = "BANK_ACCOUNT", "Bank Account"
        CREDIT_CARD = "CREDIT_CARD", "Credit Card"
        CASH = "CASH", "Cash"
        INVESTMENT = "INVESTMENT", "Investment"
        OTHER = "OTHER", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    household = models.ForeignKey(
        Household, on_delete=models.CASCADE, related_name="accounts"
    )
    name = models.CharField(max_length=100)
    account_type = models.CharField(
        max_length=20, choices=AccountType.choices, default=AccountType.BANK_ACCOUNT
    )

    institution = models.CharField(max_length=100, blank=True)
    currency = models.CharField(max_length=3, default="RS")
    balance = models.DecimalField(
        max_digits=14, decimal_place=2, default=Decimal("0.00")
    )
    created_at = models.DateTimeField(auto_add_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Financial Account"
        verbose_name_plural = "Financial Accounts"

    def __str__(self) -> str:
        return f"{self.name} ({self.account_type}) - {self.household.name}"


class AccountMember(models.Model):

    class Permission(models.TextChoices):
        OWNER = "OWNER", "Owner"
        EDITOR = "EDITOR", "Editor"
        VIEWER = "VIEWER", "Viewer"
        
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    account = models.ForeignKey(
        FinancialAccount, on_delete=models.CASCADE, related_name="members"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="account_memberships",
    )
    permission = models.CharField(
        max_length=10, choices=Permission.choices,
        default=Permission.VIEWER
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["account", "user"],
                name="unique_account_user_membership"
            )
        ]
    
    def __str__(self) -> str:
        return f"{self.user.email} - {self.permission} on {self.account.name}"