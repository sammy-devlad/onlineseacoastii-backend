from rest_framework import serializers

from account.serializers import ProfileSerializer
from baseapp.utils import ref_code
from .models import Transactions, InternationalDetails
from account.models import Account
from django.utils import timezone


class InerdetailSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = InternationalDetails
        fields = "__all__"

    def get_full_name(self, obj):
        return obj.get_fullname()


class TransactionSerializer(serializers.ModelSerializer):
    interDetail = InerdetailSerializer(read_only=True)
    sender = ProfileSerializer(read_only=True)
    receiver = ProfileSerializer(read_only=True)

    class Meta:
        model = Transactions
        fields = "__all__"


class CreateTXSBSerializer(serializers.ModelSerializer):
    account_number = serializers.CharField(required=True, max_length=100)
    beneficiary = serializers.CharField(required=True, max_length=100)

    class Meta:
        model = Transactions
        fields = ["amount", "account_number", "purpose", "beneficiary"]

    def validate(self, attrs):
        pk = int(attrs.get("beneficiary"))
        receiver = None
        try:
            receiver = Account.objects.get(pk=pk)
            print("Exist", receiver)
        except:
            receiver = None
            print("Dont exist", receiver)

        if receiver is None:
            raise serializers.ValidationError({"beneficiary": "Benneficiary not found"})
        return attrs

    def save(self, sender=None):
        pk = self.validated_data["beneficiary"]
        receiver = Account.objects.get(pk=pk)

        transaction = Transactions(
            sender=sender,
            receiver=receiver,
            purpose=self.validated_data["purpose"],
            bank_name="Onlineseacoast",
            type="Local transfer",
            invoiceRef=ref_code(),
            amount=self.validated_data["amount"],
            ben_acct=self.validated_data["account_number"],
            date=timezone.now(),
        )
        transaction.save()
        transaction.sender.balance -= transaction.amount
        transaction.sender.save()

        return transaction


class CreateTXOBSerializer(serializers.ModelSerializer):
    ben_account_number = serializers.CharField(required=True, max_length=100)
    first_name = serializers.CharField(required=True, max_length=100)
    last_name = serializers.CharField(required=True, max_length=100)
    email = serializers.EmailField(required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = Transactions
        fields = [
            "first_name",
            "last_name",
            "email",
            "ben_account_number",
            "bank_name",
            "route_num",
            "amount",
            "purpose",
        ]

    def save(self, sender=None):
        transaction = Transactions(
            sender=sender,
            purpose=self.validated_data["purpose"],
            bank_name=self.validated_data["bank_name"],
            type="Domestic transfer",
            invoiceRef=ref_code(),
            amount=self.validated_data["amount"],
            ben_acct=self.validated_data["ben_account_number"],
            route_num=self.validated_data["route_num"],
            date=timezone.now(),
        )
        details = InternationalDetails.objects.create(
            first_name=self.validated_data["first_name"],
            last_name=self.validated_data["last_name"],
            email=self.validated_data["email"],
        )
        transaction.interDetail = details
        transaction.save()
        transaction.sender.balance -= transaction.amount
        transaction.sender.save()

        return transaction


class CreateTXInSerializer(serializers.ModelSerializer):
    ben_account_number = serializers.CharField(required=True, max_length=100)
    first_name = serializers.CharField(required=True, max_length=100)
    last_name = serializers.CharField(required=True, max_length=100)
    country = serializers.CharField(
        max_length=100, required=False, allow_null=True, allow_blank=True
    )
    city = serializers.CharField(
        max_length=100, required=False, allow_null=True, allow_blank=True
    )
    # email = serializers.EmailField(required=False, allow_null=True, allow_blank=True)
    iban_number = serializers.CharField(required=True, max_length=100)
    swift_code = serializers.CharField(required=True, max_length=100)

    class Meta:
        model = Transactions
        fields = [
            "first_name",
            "last_name",
            "ben_account_number",
            "bank_name",
            "amount",
            "purpose",
            "swift_code",
            "iban_number",
            "city",
            "country",
        ]

    def save(self, sender=None):
        transaction = Transactions(
            sender=sender,
            purpose=self.validated_data["purpose"],
            bank_name=self.validated_data["bank_name"],
            type="International",
            invoiceRef=ref_code(),
            amount=self.validated_data["amount"],
            ben_acct=self.validated_data["ben_account_number"],
            date=timezone.now(),
        )
        details = InternationalDetails.objects.create(
            first_name=self.validated_data["first_name"],
            last_name=self.validated_data["last_name"],
            country=self.validated_data["country"],
            city=self.validated_data["city"],
            iban_number=self.validated_data["iban_number"],
            bic_code=self.validated_data["swift_code"],
        )
        transaction.interDetail = details
        transaction.save()
        transaction.sender.balance -= transaction.amount
        transaction.sender.save()

        return transaction


class ChangePinsserializer(serializers.ModelSerializer):
    oldpin = serializers.CharField(required=True, max_length=100)
    newpin = serializers.CharField(required=True, max_length=100)

    class Meta:
        model = Account
        fields = ["oldpin", "newpin"]

    def validate(self, attrs):
        user = self.context["request"].user
        oldpin = attrs.get("oldpin")
        newpin = attrs.get("newpin")
        if user.security_pin == newpin:
            raise serializers.ValidationError(
                {"newpin": "Security pin must be diffrent"}
            )
        if user.security_pin != oldpin:
            raise serializers.ValidationError(
                {"oldpin": "Old Security pin don't match"}
            )

        return attrs

    def save(self, **kwargs):
        user = self.context["request"].user
        user.security_pin = self.validated_data["newpin"]
        user.save()
        return user
