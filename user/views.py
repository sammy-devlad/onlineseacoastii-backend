from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db.models import Q

from account.serializers import ProfileSerializer
from .serializers import (
    ChangePinsserializer,
    TransactionSerializer,
    CreateTXSBSerializer,
    CreateTXOBSerializer,
    CreateTXInSerializer,
)
from .models import Transactions
from account.models import Account


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard(request):
    user = request.user
    transactions = Transactions.objects.filter(
        Q(sender=user) | Q(receiver=user)
    ).order_by("-date")[:5]
    TransactionReceipt = TransactionSerializer(transactions, many=True)
    return Response({"transactions": TransactionReceipt.data})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_transactions(request):
    user = request.user
    transactions = Transactions.objects.filter(
        Q(sender=user) | Q(receiver=user)
    ).order_by("-date")
    TransactionReceipt = TransactionSerializer(transactions, many=True)
    return Response({"transactions": TransactionReceipt.data})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def transaction_detail(request, pk):
    user = request.user
    transaction = get_object_or_404(Transactions, pk=pk)
    TransactionReceipt = TransactionSerializer(transaction)
    return Response({"transaction": TransactionReceipt.data})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def get_ben_name(request):
    account_number = str(request.data.get("acc_number"))
    try:
        benneficiary = Account.objects.get(username__exact=account_number)

        return Response(
            {"name": benneficiary.get_fullname(), "id": benneficiary.id, "valid": True}
        )
    except Account.DoesNotExist:
        benneficiary = None

        return Response({"error": "Not Found"})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def transferSb(request):
    print(request.data)
    user = request.user
    serializer = CreateTXSBSerializer(data=request.data)
    amount = int(request.data["amount"])
    if user.balance >= amount:
        if serializer.is_valid():
            tx = serializer.save(user)
            TransactionReceipt = TransactionSerializer(tx)
            return Response({"error": False, "tx": TransactionReceipt.data})
        else:
            return Response({"error": True, "msg": "Unknown error just occurred"})
    else:
        return Response({"error": True, "msg": "insufficent funds"})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def transferOb(request):
    user = request.user
    serializer = CreateTXOBSerializer(data=request.data)
    amount = int(request.data["amount"])
    if user.balance >= amount:
        if serializer.is_valid():
            tx = serializer.save(user)
            TransactionReceipt = TransactionSerializer(tx)
            return Response({"error": False, "tx": TransactionReceipt.data})
        else:
            print(serializer.errors)
            return Response({"error": True, "msg": "Unknown error just occurred"})
    else:
        return Response({"error": True, "msg": "insufficent funds"})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def transferIn(request):
    user = request.user
    serializer = CreateTXInSerializer(data=request.data)
    amount = int(request.data["amount"])
    if user.balance >= amount:
        if serializer.is_valid():
            tx = serializer.save(user)
            TransactionReceipt = TransactionSerializer(tx)
            return Response({"error": False, "tx": TransactionReceipt.data})
        else:
            print(serializer.errors)
            return Response({"error": True, "msg": "Unknown error just occurred"})
    else:
        return Response({"error": True, "msg": "insufficent funds"})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def resetPin(request):
    user = request.user
    serializer = ChangePinsserializer(
        instance=user, data=request.data, context={"request": request}
    )
    if serializer.is_valid():
        instance = serializer.save()
        profile = ProfileSerializer(instance)
        return Response({"error": False, "user": profile.data, "msg": "Sucessful"})
    else:
        print(serializer.errors)
        return Response({"error": True, "msg": serializer.errors})
