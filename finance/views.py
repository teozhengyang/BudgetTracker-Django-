import decimal
from django.db import IntegrityError
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django import forms
from .models import User, Transaction, Goal, Investment
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
import pyEX as p
import json

# using IEX cloud API for investment products quote
c = p.Client(api_token='pk_c0d08e48b0d7449797907ef04c464b22', version='stable')

# register new user form
class RegisterForm(forms.Form):
    username = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    email = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Email'}))
    password = forms.CharField( required=True, widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    confirm_password = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}))

# login form
class LoginForm(forms.Form):
    username = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    password = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))

transaction_accounts = [
    ("Budget", "Budget"),
    ("Savings", "Savings")
]    

# Add income form
class IncomeForm(forms.Form):
    account = forms.ChoiceField(label="Account",choices=transaction_accounts, required=True)
    amount = forms.DecimalField(label="Amount", required=True, max_digits=18, decimal_places=2)
    description = forms.CharField(label="Description", required=True,widget=forms.Textarea(attrs={"rows":2, "cols": 30}))
    
# Add expense form
class ExpenseForm(forms.Form):
    account = forms.ChoiceField(label="Account",choices=transaction_accounts, required=True)
    amount = forms.DecimalField(label="Amount", required=True, max_digits=18, decimal_places=2)
    description = forms.CharField(label="Description", required=True,widget=forms.Textarea(attrs={"rows":2, "cols": 30}))

# Add transfer form
class TransferForm(forms.Form):
    source = forms.ChoiceField(label="Source",choices=transaction_accounts, required=True)
    destination = forms.ChoiceField(label="Destination",choices=transaction_accounts, required=True)
    amount = forms.DecimalField(label="Amount", required=True, max_digits=18, decimal_places=2)
    description = forms.CharField(label="Description", required=True,widget=forms.Textarea(attrs={"rows":2, "cols": 30}))

# Add goal form
class GoalForm(forms.Form):
    account = forms.ChoiceField(label="Account",choices=transaction_accounts, required=True)
    amount = forms.DecimalField(label="Amount", required=True, max_digits=18, decimal_places=2)
    description = forms.CharField(label="Description", required=True,widget=forms.Textarea(attrs={"rows":2, "cols": 30}))

# Add investment form
class InvestmentForm(forms.Form):
    symbol = forms.CharField(label="Symbol", required=True)
    account = forms.ChoiceField(label="Account",choices=transaction_accounts, required=True)
    amount = forms.DecimalField(label="Total Amount Spent", required=True, max_digits=20, decimal_places=2)
    number = forms.DecimalField(label="Number of Shares", required=True, max_digits=20, decimal_places=2)

# index view (see entire portfolio)
def index(request):
    # when user is logged in
    if request.user.is_authenticated:
        user = User.objects.get(username=request.user.username)
        investment_worth = 0
        portfolio = Investment.objects.filter(owner=user)
        # update current value of all products in portfolio
        for product in portfolio:
            data = c.quote(symbol=product.symbol)
            product.value = float(data['latestPrice'])
            product.save()
            product.total_value = round((decimal.Decimal(product.value) * product.number), 2)
            product.save()
            investment_worth += product.total_value
        # update user investments' value
        user.investment = investment_worth
        user.save()
        user.net_worth = user.budget + user.savings + user.investment
        user.save()
        recent_transactions = Transaction.objects.filter(owner=user).order_by("-timestamp")[:10]
        return render(request, "finance/index.html", {
            "user": user,
            "transactions": recent_transactions
        })
    # for user not logged in
    return HttpResponseRedirect(reverse("login"))

# login view
def login_user(request):
    # when user submit login form
    if request.method == "POST":
        # access username and pw user has typed in
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            # attempt to sign user in
            user = authenticate(request, username=username, password=password)
            # check if authentication successful
            if user is not None:
                login(request, user)
                return HttpResponseRedirect(reverse("index"))
            else: 
                return render(request, "finance/error.html", {
                    "message": "Invalid username and/or password"
                })
    # when user want to login
    else:
        return render(request, "finance/login.html", {
        "form": LoginForm,
    })

# logout view
def logout_user(request):
    logout(request)
    return HttpResponseRedirect(reverse("login"))

# register view
def register(request):
    # when user submit register form
    if request.method == "POST":
        # access username, email, pw user has typed in
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            confirm_password = form.cleaned_data["confirm_password"]
            # ensure both pw matches
            if password != confirm_password:
                return render(request, "finance/error.html", {
                    "message": "Passwords must match."
                })
            # attempt to create new user
            try:
                user = User.objects.create_user(username, email, password)
                user.save()
            except IntegrityError:
                return render(request, "finance/error.html", {
                    "message": "Username already taken."
                })
            # log user in if successful
            login(request, user)
            # return index page
            return HttpResponseRedirect(reverse("index"))
    else:
        # when new user want to register
        return render(request, "finance/register.html", {
        "form": RegisterForm,
    })
        
# investment index view
def investment(request):
    user = User.objects.get(username=request.user.username)
    transactions = Transaction.objects.filter(owner=user, type="Investment").order_by("-timestamp")
    # paginate all transactions by 10 per pages
    paginator = Paginator(transactions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    portfolio = Investment.objects.filter(owner=user)
    # update current value of all products in portfolio
    for product in portfolio:
        data = c.quote(symbol=product.symbol)
        product.value = float(data['latestPrice'])
        product.save()
        product.total_value = round((decimal.Decimal(product.value) * product.number), 2)
        product.save()
    return render(request, "finance/investment.html", {
        "page_obj": page_obj,
        "portfolio": portfolio
    })

# purchase investment view
def add_investment(request):
    if request.method == "POST":
        # when user submit new investment form
        form = InvestmentForm(request.POST)
        if form.is_valid():
            # access account, symbol, amount, number user has typed in
            account = form.cleaned_data["account"]
            symbol = form.cleaned_data["symbol"]
            number = form.cleaned_data["number"]
            amount = form.cleaned_data["amount"]
            user = User.objects.get(username=request.user.username)
            # product's symbol exists
            try:
                data = c.quote(symbol=symbol)
            # product's symbol does not exist
            except:
                return render(request, "finance/error.html", {
                    "message": "No such symbol!"
                })
            # edit user's relevant account
            if account == "Budget":
                # reject if amount spent more than account amount
                if amount > user.budget:
                    return render(request, "finance/error.html", {
                        "message": "Insufficient amount in account" 
                    })
                else:
                    user.budget -= amount
            elif account == "Savings":
                # reject if amount spent more than account amount
                if amount > user.savings:
                    return render(request, "finance/error.html", {
                        "message": "Insufficient amount in account" 
                    })
                else:
                    user.savings -= amount
            user.investment += amount
            user.save()
            # add as transaction
            type = "Investment"
            description = f'Purchase of {number} share(s) of {symbol} for ${amount}'
            transaction = Transaction(owner=user, type=type, account=account, amount=amount, description=description)
            transaction.save() 
            try:
                # check whether product added is new product in user's portfolio
                product = Investment.objects.get(owner=user, symbol=symbol)
                # edit number and amount of product in portfolio
                product.number += number
                product.amount += amount
                product.save()
            # product does not exist in portfolio
            except Investment.DoesNotExist:
                new_product = Investment(owner=user, symbol=symbol, number=number, amount=amount)
                new_product.save()
        # redirect user to investment index
        return HttpResponseRedirect(reverse("investment"))
    # when user wants to submit new investment form
    else:
        return render(request, "finance/addinvestment.html", {
            "form": InvestmentForm
        })
    
# sell investment view
def sell_investment(request):
    if request.method == "POST":
        # when user submit new investment form
        form = InvestmentForm(request.POST)
        if form.is_valid():
            # access account, symbol, amount, number user has typed in
            account = form.cleaned_data["account"]
            symbol = form.cleaned_data["symbol"]
            number = form.cleaned_data["number"]
            amount = form.cleaned_data["amount"]
            user = User.objects.get(username=request.user.username)
            # check that product's symbol exists
            try:
                data = c.quote(symbol=symbol)
            # product's symbol does not exist
            except:
                return render(request, "finance/error.html", {
                    "message": "No such symbol!"
                })
            # check product in user's portfolio 
            try:
                product = Investment.objects.get(owner=user, symbol=symbol)
            except Investment.DoesNotExist:
                return render(request, "finance/error.html", {
                    "message": "Product does not exist in your portfolio!"
                })
            # check if number of shares sold more than number of shares owned
            if product.number < number:
                return render(request, "finance/error.html", {
                    "message": "Number of shares sold exceeded number of shares owned!"
                })
            else:
                product_average_price = product.amount / product.number
                product.number -= number
                product.save()
                product.amount = product_average_price * product.number 
                product.save()
                if account == "Budget":
                    user.budget += amount
                    user.save()
                if account == "Savings":
                    user.savings += amount
                    user.save()
                # add as transaction
                type = "Investment"
                description = f'Sale of {number} share(s) of {symbol} for ${amount}'
                transaction = Transaction(owner=user, type=type, account=account, amount=amount, description=description)
                transaction.save() 
        # redirect user to investment index
        return HttpResponseRedirect(reverse("investment"))
    # when user wants to submit new sale of investment form
    else:
        return render(request, "finance/sellinvestment.html", {
            "form": InvestmentForm
        })

# goals index view
def goals(request):
    # access user
    user = User.objects.get(username=request.user.username)
    # access all goals of user
    goals = Goal.objects.filter(owner=user).order_by("-timestamp")
    # update goals' progress if needed
    for goal in goals:
        if goal.account == "Budget":
            goal.progress = round((user.budget / goal.amount * 100) , 2)
            if goal.progress > 100:
                goal.progress = 100
        goal.save()
        if goal.account == "Savings":
            goal.progress = round((user.savings / goal.amount * 100), 2)
            if goal.progress > 100:
                goal.progress = 100
        goal.save()
    # render goals page
    return render(request, "finance/goals.html", {
        "form": GoalForm,
        "goals": goals
    })

# individual goal view
@csrf_exempt
def goal(request, goal_id):
    # access post
    try:
        goal = Goal.objects.get(pk=goal_id)
    except Goal.DoesNotExist:
        return JsonResponse({
            "error": "Goal Not Found"
        }, status=404)
    
    # when post's url type in manually
    if request.method == "GET":
        return JsonResponse(goal.serialize())

    # when user want to edit or delete post
    elif request.method == "PUT":
        data = json.loads(request.body)
        # for user to delete goal
        if data.get("delete"):
            goal.delete()
        # for user to edit goal and access any new information about goal
        else: 
            if data.get("newaccount"):
                goal.account = data["newaccount"]
            if data.get("newamount"):
                goal.amount = data["newamount"]
            if data.get("newdescription"):
                goal.description = data["newdescription"]
            goal.save()
        return HttpResponse(status=204) 
            
    # return error if not GET or PUT request
    else:
        return JsonResponse({
            "error": "GET or PUT request required"
        }, status=400)

# add goal view
def add_goal(request):
    # when user submit new goal form
    if request.method == "POST":
        form = IncomeForm(request.POST)
        if form.is_valid():
            # access account, amount, description user has typed in
            account = form.cleaned_data["account"]
            amount = form.cleaned_data["amount"]
            description = form.cleaned_data["description"]
            user = User.objects.get(username=request.user.username)
            if account == "Budget":
                progress = round((user.budget / amount * 100), 2)
                if progress > 100:
                    progress = 100
            if account == "Savings":
                progress = round((user.savings / amount * 100), 2)
                if progress > 100:
                    progress = 100
            goal = Goal(owner=user, account=account, amount=amount, description=description, progress=progress)
            # add goal
            goal.save()
        # return user to goals page
        return HttpResponseRedirect(reverse("goals"))
    else:
        return HttpResponseRedirect(reverse("goals"))

# add income view
def add_income(request):
    # when user submit new income transaction form
    if request.method == "POST":
        form = IncomeForm(request.POST)
        if form.is_valid():
            # access account, amount, description user has typed in
            account = form.cleaned_data["account"]
            amount = form.cleaned_data["amount"]
            description = form.cleaned_data["description"]
            type = "Income"
            user = User.objects.get(username=request.user.username)
            transaction = Transaction(owner=user, type=type, account=account, amount=amount, description=description)
            # add income transaction
            transaction.save()
            # edit user account involved and net worth
            if account == "Budget":
                user.budget += amount
                user.net_worth += amount
                user.save()
                goals = Goal.objects.filter(owner=user)
                for goal in goals:
                    if goal.account == "Budget":
                        goal.progress = user.budget / goal.amount * 100
                        if goal.progress > 100:
                            goal.progress = 100
                        goal.save()
            if account == "Savings":
                user.savings += amount
                user.net_worth += amount
                user.save()
                goals = Goal.objects.filter(owner=user)
                for goal in goals:
                    if goal.account == "Savings":
                        goal.progress = user.savings / goal.amount * 100
                        if goal.progress > 100:
                            goal.progress = 100
                        goal.save()
            # return user to homepage
            return HttpResponseRedirect(reverse("index"))
    # when user wants to submit new income transaction
    else:
        return render(request, "finance/addincome.html", {
            "form": IncomeForm
        })

# add expense view
def add_expense(request):
    if request.method == "POST":
        # when user submit new expense transaction form
        form = ExpenseForm(request.POST)
        if form.is_valid():
            # access account, amount, description user has typed in
            account = form.cleaned_data["account"]
            amount = form.cleaned_data["amount"]
            description = form.cleaned_data["description"]
            type = "Expense"
            user = User.objects.get(username=request.user.username)
            transaction = Transaction(owner=user, type=type, account=account, amount=amount, description=description)
            # add expense transaction
            transaction.save()
            # edit user account involved and net worth
            if account == "Budget":
                user.budget -= amount
                user.net_worth -= amount
                user.save()
                goals = Goal.objects.filter(owner=user)
                for goal in goals:
                    if goal.account == "Budget":
                        goal.progress = user.budget / goal.amount * 100
                        if goal.progress > 100:
                            goal.progress = 100
                        goal.save()
            elif account == "Savings":
                user.savings -= amount
                user.net_worth -= amount
                user.save()
                goals = Goal.objects.filter(owner=user)
                for goal in goals:
                    if goal.account == "Budget":
                        goal.progress = user.savings / goal.progress * 100
                        if goal.progress > 100:
                            goal.progress = 100
                        goal.save()
            # return user to homepage
            return HttpResponseRedirect(reverse("index"))
    # when user wants to submit new expense transaction
    else:
        return render(request, "finance/addexpense.html", {
            "form": ExpenseForm
        })

# transfer between budget and savings account
def add_transfer(request):
    if request.method == "POST":
        # when user submit new transfer transaction form
        form = TransferForm(request.POST)
        if form.is_valid():
            # access source, destination, amount, description user has typed in
            source = form.cleaned_data["source"]
            destination = form.cleaned_data["destination"]
            amount = form.cleaned_data["amount"]
            description = form.cleaned_data["description"]
            type = "Transfer"
            if source == destination:
                return render(request, "finance/error.html", {
                    "message": "Source and Destination accounts must be different."
                })
            account = f"{source} to {destination}"
            user = User.objects.get(username=request.user.username)
            # edit user accounts involved 
            if source == "Budget":
                if user.budget < amount:
                    return render(request, "finance/error.html", {
                    "message": "Insufficient amount in source account"
                }) 
                user.budget -= amount
                user.savings += amount
                user.save()
                goals = Goal.objects.filter(owner=user)
                for goal in goals:
                    if goal.account == "Budget":
                        goal.progress = user.budget / goal.amount * 100
                        if goal.progress > 100:
                            goal.progress = 100
                        goal.save()
                    elif goal.account == "Savings":
                        goal.progress = user.savings / goal.amount * 100
                        if goal.progress > 100:
                            goal.progress = 100
                        goal.save()
            if source == "Savings":
                if user.savings < amount:
                    return render(request, "finance/error.html", {
                    "message": "Insufficient amount in source account"
                })
                user.savings -= amount
                user.budget += amount
                user.save()
                goals = Goal.objects.filter(owner=user)
                for goal in goals:
                    if goal.account == "Budget":
                        goal.progress = user.budget / goal.amount * 100
                        if goal.progress > 100:
                            goal.progress = 100
                        goal.save()
                    elif goal.account == "Savings":
                        goal.progress = user.savings / goal.amount * 100
                        if goal.progress > 100:
                            goal.progress = 100
                        goal.save()
            transaction = Transaction(owner=user, type=type, account=account, amount=amount, description=description)
            # add transfer transaction
            transaction.save()
            # return user to homepage
            return HttpResponseRedirect(reverse("index"))
    # when user wants to submit new transfer transaction
    else:
        return render(request, "finance/addtransfer.html", {
            "form": TransferForm
        })

# all transactions view
def transactions(request):
    # access user
    user = User.objects.get(username=request.user.username)
    # access all transactions of user
    all_transactions = Transaction.objects.filter(owner=user).order_by("-timestamp")
    # paginate all transactions by 15 per pages
    paginator = Paginator(all_transactions, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    # render transactions page
    return render(request, "finance/transactions.html", {
        "page_obj": page_obj
    })
    
# calculator page
def calculator(request):
    return render(request, "finance/calculator.html")