from django.contrib import admin
from .models import Transaction, User, Goal, Investment

# display User in admin interface
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "email", "budget", "savings", "investment", "net_worth")
# display transaction in admin interface
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("owner", "type", "account", "amount", "description", "timestamp")
# display goal in admin interface
class GoalAdmin(admin.ModelAdmin):
    list_display = ("owner", "account", "amount", "description", "progress", "timestamp")
# display investment in admin interface
class InvestmentAdmin(admin.ModelAdmin):
    list_display = ("owner", "symbol", "number", "amount", "value", "total_value")


# register User, Transaction
admin.site.register(User, UserAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Goal, GoalAdmin)
admin.site.register(Investment, InvestmentAdmin)