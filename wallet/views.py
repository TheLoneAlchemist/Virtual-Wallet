from django.db.models import Q
import decimal
from django.shortcuts import render, redirect
from .form import WalletUserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Transaction, TransactionRequest, User



def Index(request):
    return render(request, "index.html")


def Register(request):
    if request.method == "POST":
        form = WalletUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            print(user)
            messages.success(request, f"User {user} has been created!")
            if user is not None:
                login(request, user)
                return redirect('/wallet')
            else:
                return redirect('/login')

    else:
        form = WalletUserCreationForm()

    return render(request, 'register.html', {'form': form})


def Login(request):

    if request.method == "POST":
        Username = request.POST.get('username')
        Password = request.POST.get('password')
        print(Username, Password)

        # user = User.objects.filter(username=Username).first()
        # print("===",user)
        user = authenticate(username=Username, password=Password)
        print("===", user)

        if user is not None:
            login(request, user)
            messages.success(request, f"Hii! Welcome Back {user}")
            return redirect("/")
        else:
            messages.error(
                request, "You enterd wrong details!, Kindly put right information.")
            return redirect("login")

    return render(request, 'login.html')


def Logout(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('/login')


def Wallet(request):
    if request.user.is_authenticated:

        #transactions = Transaction.objects.filter(Q(sender= request.user) | Q(receiver = request.user))
        from django.db.models import F

        sent_transactions = Transaction.objects.filter(sender=request.user)
        received_transactions = Transaction.objects.filter(
            receiver=request.user)

        transactions = (sent_transactions.annotate(date=F('transaction_date'))
                        .union(received_transactions.annotate(date=F('transaction_date')))
                        .order_by('-date'))

        print(transactions)

        return render(request, "wallet.html", {'balance': request.user.wallet_balance, 'transactions': transactions})
    return redirect('/login')


def Transct(Sender, Reciever, superuser, amount, Remark):

    Sender_wallet_balance = Sender.wallet_balance
    Reciever_wallet_balance = Reciever.wallet_balance
    print(Sender.is_premium)
    # sender balanace calculation
    if(Sender.is_premium):
        sender_charges = decimal.Decimal('0.03')
    else:
        sender_charges = decimal.Decimal('0.05')
  
    print(f"sender {Sender} balance: ", Sender.wallet_balance)
    
    Sender.wallet_balance = Sender.wallet_balance - ((amount * sender_charges) + amount)

    Sender.save(update_balance=True)
    print(f"sender {Sender} balance: ", Sender.wallet_balance)
    # reciever balalance calculation

    if(Reciever.is_premium):
        reciever_charges = decimal.Decimal('0.03')
    else:
        reciever_charges = decimal.Decimal('0.05')
    Reciever.wallet_balance = Reciever.wallet_balance + ( amount - (amount * reciever_charges))
    Reciever.save(update_balance=True)
    print(f"Reciever {Reciever} balance: ", Reciever.wallet_balance)

    # added superuser balalance

    superuser.wallet_balance = superuser.wallet_balance + (amount * reciever_charges)
    print(f"superuser {superuser} balance: ", superuser.wallet_balance)
    superuser.save(update_balance= True)

    transanctionobj = Transaction.objects.create(sender=Sender, receiver=Reciever, amount=amount, sender_remain_amount=Sender.wallet_balance, reciever_remain_amount=Reciever.wallet_balance,transaction_type='send', sender_transaction_charge=sender_charges, reciever_transaction_charge=reciever_charges, remarks=Remark)
    transanctionobj.save()


def SendMoney(request):

    if request.user.is_authenticated:

        if request.method == "POST":
            Reciever = request.POST['user']
            amount = decimal.Decimal(request.POST['amount'])
            Remark = request.POST['remark']

            try:
                Sender = User.objects.get(username=request.user)
                Reciever = User.objects.get(username=Reciever)
                superuser = User.objects.get(username='admin')
                if (amount > Sender.wallet_balance):
                    messages.error(request, "Inffsuficiate balance")
                    return redirect('/sendmoney')
                Transct(Sender, Reciever, superuser, amount, Remark)
            except Exception as e:
                print(e)
            finally:
                return redirect('/sendmoney')

        users = User.objects.exclude(
            id=request.user.id).exclude(username='admin')
        return render(request, 'sendmoney.html', {'users': users})

    return redirect('/login')


def RequestMoney(request):

    if request.user.is_authenticated:
        if request.method == "POST":
            Reciever = request.POST['user']
            amount = decimal.Decimal(request.POST['amount'])

            Sender = User.objects.get(username=request.user)
            Reciever = User.objects.get(username=Reciever)

            TransactionRequestObj = TransactionRequest.objects.create(
                sender=Sender, receiver=Reciever, amount=amount, status="pending")

            TransactionRequestObj.save()
            messages.success(request, "Request has been sent!")
            return redirect('/requestmoney')

        users = User.objects.exclude(
            id=request.user.id).exclude(username='admin')
        return render(request, 'requestmoney.html', {'users': users})

    return redirect('/login')


def RequestLog(request):

    if request.user.is_authenticated:

        if request.method == 'POST':
            try:
                if 'accept' in request.POST:
                    request_pk = request.POST['accept']
                    TransactionRequestObj = TransactionRequest.objects.get(pk=request_pk)
                    Sender = request.user
                    Reciever = User.objects.get(username=TransactionRequestObj.sender)
                    amount = TransactionRequestObj.amount
                    Remark = "Sent"
                    superuser = User.objects.get(username='admin')
                    if (amount > Sender.wallet_balance):
                        messages.error(request, "Inffsuficiate balance")
                        return redirect('/requestlog')
                    Transct(Sender, Reciever, superuser, amount, Remark)
                    TransactionRequestObj.status = 'accepted'
                    TransactionRequestObj.save()
                elif 'decline' in request.POST:
                    
                    request_pk = request.POST['decline']
                    TransactionRequestObj = TransactionRequest.objects.get(pk=request_pk)
                    TransactionRequestObj.status = 'declined'
                    TransactionRequestObj.save()

            except Exception as e:
                print(e)
            return redirect('/requestlog')

        requestes = TransactionRequest.objects.filter(
            receiver=request.user).exclude(sender=request.user)
        print(requestes)
        return render(request, 'requestlog.html', {'requestes': requestes})
    return redirect('/login')
