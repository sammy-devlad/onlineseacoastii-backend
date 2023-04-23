from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from account.models import Account
from superuser.decorator import superuser_required
from superuser.forms import LocalTxForms, DomesticTxForms, InterTxForms
from user.models import Transactions
from baseapp import utils
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import get_template
from django.utils import timezone
from django.db.models import Q


@superuser_required
def dashboard(request):
    total_balance = 0
    for acc in Account.objects.all():
        total_balance += acc.balance

    context = {
        "total_balance": total_balance,
        "users": Account.objects.all().count(),
        "transactions": Transactions.objects.all().count(),
        "com_transaction": Transactions.objects.filter(
            status=utils.STATUS["SUCCESS"]
        ).count(),
        "pending_transaction": Transactions.objects.filter(
            status=utils.STATUS["PENDING"]
        ).count(),
    }
    return render(request, "superuser/index.html", context)


@superuser_required
def users_(request):
    search_post = request.GET.get("search")
    if search_post:
        users = Account.objects.filter(
            Q(first_name__icontains=search_post) | Q(email__icontains=search_post)
        ).order_by("-last_login")
    else:
        users = Account.objects.all().order_by("-last_login")
    return render(request, "superuser/users.html", {"users": users})


@superuser_required
def user_detail(request, pk):
    account = get_object_or_404(Account, pk=pk)
    amount_sent = 0
    amount_received = 0

    for trxS in Transactions.objects.filter(sender=account):
        amount_sent += trxS.amount
    for trxR in Transactions.objects.filter(receiver=account):
        amount_received += trxR.amount

    if request.POST:
        amount = int(request.POST.get("amount"))
        submit = request.POST.get("submit")
        if submit == "Top up":
            account.balance += amount
            account.save()

            # mail
            current_site = get_current_site(request)
            subject = "Account Credited"
            context = {
                "name": account.get_fullname(),
                "domain": current_site.domain,
                "amount": amount,
                "date": timezone.now(),
            }
            message = get_template("superuser/topup.email.html").render(context)
            mail = EmailMessage(
                subject=subject,
                body=message,
                from_email=utils.EMAIL_ADMIN,
                to=[account.email],
                reply_to=[utils.EMAIL_ADMIN],
            )
            mail.content_subtype = "html"
            mail.send(fail_silently=True)
            # mail ends
            messages.success(request, "Account Top Up Successful")
            return redirect("admin-users-details", pk=account.id)
        else:
            messages.success(request, "Something went wrong")
            return redirect("admin-users")

    context = {
        "account": account,
        "amount_sent": amount_sent,
        "amount_received": amount_received,
    }

    return render(request, "superuser/user_detail.html", context)


@superuser_required
def transactions_(request):
    transactions = Transactions.objects.all().order_by("-date")
    return render(
        request, "superuser/transactions.html", {"transactions": transactions}
    )


@superuser_required
def transactions_details(request, pk):
    transaction = get_object_or_404(Transactions, pk=pk)
    current_site = get_current_site(request)
    if request.POST:
        submit_type = request.POST.get("submit")
        if submit_type == "approve":
            transaction.status = utils.STATUS["SUCCESS"]
            transaction.save()
            if transaction.receiver:
                transaction.receiver.balance += transaction.amount
                transaction.receiver.save()
                # mail
                utils.alertTx(
                    transaction,
                    current_site,
                    "Transaction Alert",
                    "Credited",
                    transaction.receiver.email,
                    transaction.receiver.get_fullname(),
                )
                # mail ends
            # mail
            utils.alertTx(
                transaction,
                current_site,
                "Transaction Alert",
                "Debited",
                transaction.sender.email,
                transaction.sender.get_fullname(),
            )
            # mail ends
            messages.info(request, "Transaction approved")
            return redirect("admin-transactions_details", pk=pk)
        elif submit_type == "decline":
            transaction.status = utils.STATUS["DECLINED"]
            transaction.save()
            # mail
            current_site = get_current_site(request)
            subject = "Transaction Faild"
            context = {
                "name": transaction.sender.get_fullname(),
                "domain": current_site.domain,
                "tx": transaction,
                "ty_pe": "Declined",
            }

            message = get_template("superuser/txprocessdecline.email.html").render(
                context
            )
            mail = EmailMessage(
                subject=subject,
                body=message,
                from_email=utils.EMAIL_ADMIN,
                to=[transaction.sender.email],
                reply_to=[utils.EMAIL_ADMIN],
            )
            mail.content_subtype = "html"
            mail.send(fail_silently=True)
            # mail ends
            messages.info(request, "Transaction Declined")
            return redirect("admin-transactions_details", pk=pk)
        else:
            messages.info(request, "An unknown error occured")
            return redirect("admin-transactions_details", pk=pk)

    return render(
        request, "superuser/transaction_details.html", {"transaction": transaction}
    )


@superuser_required
def create_transaction(request):
    user = request.user
    if request.POST:
        form = LocalTxForms(user=user, data=request.POST)
        if form.is_valid():
            instance = form.save()
            messages.info(request, "Transaction Created")
            return redirect("admin-transactions_details", pk=instance.id)
    else:
        form = LocalTxForms(user=user)
    return render(request, "superuser/createTx.html", {"form": form})


@superuser_required
def create_transactionOB(request):
    user = request.user
    if request.POST:
        form = DomesticTxForms(user=user, data=request.POST)
        if form.is_valid():
            instance = form.save()
            messages.info(request, "Transaction Created")
            return redirect("admin-transactions_details", pk=instance.id)
    else:
        form = DomesticTxForms(user=user)
    return render(request, "superuser/createTxOB.html", {"form": form})


@superuser_required
def create_transactionIN(request):
    user = request.user
    if request.POST:
        form = InterTxForms(user=user, data=request.POST)
        if form.is_valid():
            instance = form.save()
            messages.info(request, "Transaction Created")
            return redirect("admin-transactions_details", pk=instance.id)
    else:
        form = InterTxForms(user=user)
    return render(request, "superuser/createTxIN.html", {"form": form})
