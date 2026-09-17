import uuid
from decimal import Decimal
from django.conf import settings
from django.db import models
from accounts.models import FinancialAccount
from households.models import Household

# Create your models here.

class Category(models.Model):
    class CategoryType(models.TextChoices):
        INCOME = "INCOME", "Income"
        EXPENSES = "EXPENSES", "Expenses"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    household = models.ForeignKey(
        Household,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="categories",
    )

    name = models.CharField(max_length=50)
    category_type = models.CharField(
        max_length=10,
        choices=CategoryType.choices,
        default=CategoryType.EXPENSES,
    )

    icon = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Category"
        verbose_name_plural = "categories"

    def __str__(self) -> str:
        prefix = f"[{self.household.name}] " if self.household else " [Global] "
        return f"{prefix}{self.name} ({self.category_type})"



class Transaction(models.Model):
    class TransactionType(models.TextChoices):
        INCOME = "INCOME", "Income"
        EXPENSES = "EXPENSES", "Expenses"
        TRANSFER = "TRANSFER", "Transfer"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    account = models.ForeignKey(
        FinancialAccount,
        on_delete=models.CASCADE,
        related_name ="transactions"
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions",
    )

    amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))

    transaction_type = models.CharField(
        max_length=10,
        choices=TransactionType.choices,
        default=TransactionType.EXPENSES
    )

    description = models.CharField(max_length=255)
    merchant = models.CharField(max_length=10, blank=True)
    transaction_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-transaction_date", "-created_at"]
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"

    def __str__(self) -> str:
        return f"{self.transaction_date} | {self.transaction_type}: {self.amount} - {self.description}"