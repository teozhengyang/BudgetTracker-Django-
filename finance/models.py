from django.db import models
from django.contrib.auth.models import AbstractUser

transaction_types = [
    ("Income", "Income"),
    ("Expense", "Expense"),
    ("Transfer", "Transfer"),
    ("Investment", "Investment"),
]

accounts = [
    ("Budget", "Budget"),
    ("Savings", "Savings"),
    ("Budget to Savings", "Budget to Savings"),
    ("Savings to Budget", "Savings to Budget")
]

# User model
class User(AbstractUser):
    budget = models.DecimalField(default=0, null=True, max_digits=20, decimal_places=2)
    savings = models.DecimalField(default=0, null=True, max_digits=20, decimal_places=2)
    investment = models.DecimalField(default=0, null=True, max_digits=20, decimal_places=2)
    net_worth = models.DecimalField(default=0, null=True, max_digits=20, decimal_places=2)
    def __str__(self):
        return f"{self.username}"

# Transaction
class Transaction(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transaction")
    type = models.CharField(choices=transaction_types,blank=True, max_length=30)
    account = models.CharField(choices=accounts,blank=True, max_length=30)
    amount = models.DecimalField(default=0, null=True, max_digits=20, decimal_places=2)
    description = models.TextField(null=True)
    timestamp = models.DateTimeField(auto_now_add=True, null=True)
    
# Goal
class Goal(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="goal")
    account = models.CharField(choices=accounts,blank=True, max_length=30)
    amount = models.DecimalField(default=0, null=True, max_digits=20, decimal_places=2)
    description = models.TextField(null=True)
    progress = models.DecimalField(null=True, max_digits=20, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True, null=True)
    
    def serialize(self):
        return {
            "owner": self.owner.username,
            "account": self.account,
            "amount": self.amount,
            "description": self.description,
            "progress": self.progress,
            "timestamp": self.timestamp
        }
    
class Investment(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="invested_product")
    symbol = models.CharField(max_length=50)
    number = models.DecimalField(null=True, max_digits=20, decimal_places=2)
    amount = models.DecimalField(null=True, max_digits=20, decimal_places=2)
    value = models.DecimalField(null=True, max_digits=20, decimal_places=2)
    total_value = models.DecimalField(null=True, max_digits=20, decimal_places=2)