import uuid
from decimal import Decimal
from django.conf import settings
from django.db import models
from households.models import Household
from transactions.models import Category

# Create your models here.

class Budget(models.Model):
    class Period(models.Model):
        MONTHLY = "MONTHLY", "Monthly"
        YEARLY = "YEARLY", "Yearly"
        CUSTOM = "CUSTOM", "Custom"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    household = models.ForeignKey(
        Household,
        on_delete=models.CASCADE,
        related_name="budgets",
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="budgets"
    )

    amount = models.DecimalField(
        max_digits=14, decimal_places=2, default=Decimal("0.00")
    )

    period = models.CharField(
        max_length=10,
        choices=Period.choices,
        default=Period.MONTHLY,
    )

    start_date = models.DateField()
    end_date = models.DateField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_budgets"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-start_date"]
        verbose_name = "Budget"
        verbose_name_plural = "Budgets"
        
    def __str__(self) -> str:
        return f"{self.household.name} - {self.category.name}: {self.amount} ({self.period})"