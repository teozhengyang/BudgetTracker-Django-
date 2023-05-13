from django.urls import path
from . import views

urlpatterns = [
    # budget & savings index path
    path("", views.index, name="index"),
    
    # login, logout, register paths
    path("login", views.login_user, name="login"),
    path("logout", views.logout_user, name="logout"),
    path("register", views.register, name="register"),
    
    # investment index, add investment, sell investment path
    path("investment", views.investment, name="investment"),
    path("addinvestment", views.add_investment, name="addinvestment"),
    path("sellinvestment", views.sell_investment, name="sellinvestment"),
    
    # goals index, individual goal, add goal path
    path("goals", views.goals, name="goals"),
    path("goals/<int:goal_id>", views.goal, name="goal"),
    path("addgoal", views.add_goal, name="addgoal"),
    
    # add income, expense, transfer path
    path("addincome", views.add_income, name="addincome"),
    path("addexpense", views.add_expense, name="addexpense"),
    path("addtransfer", views.add_transfer, name="addtransfer"),
    
    # view all transactions path
    path("transactions", views.transactions, name="transactions"),
    
    # calculator path
    path("calculator", views.calculator, name="calculator"),
]
