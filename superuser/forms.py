from django import forms

from user.models import Transactions, InternationalDetails
from account.models import Account
from baseapp import utils


class LocalTxForms(forms.ModelForm):
    receiver_acct_num = forms.CharField(
        max_length=50,
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control",
                "placeholder": "Recipient account number",
            }
        ),
        label="Recipient",
        required=True,
    )

    purpose = forms.CharField(
        max_length=200,
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control form-control-lg",
                "placeholder": "brief description",
            }
        ),
        label="Purpose",
        required=True,
    )

    dateCreated = forms.DateTimeField(
        widget=forms.widgets.DateTimeInput(
            format="%Y-%m-%d %H:%M",
            attrs={
                "type": "datetime-local",
                "class": "form-control form-control-lg",
            },
        ),
        label="Date created",
        required=True,
    )

    class Meta:
        model = Transactions
        fields = ["receiver_acct_num", "amount", "purpose", "dateCreated"]

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_receiver_acct_num(self):
        recipient = self.cleaned_data["receiver_acct_num"]
        account = None
        try:
            account = Account.objects.get(username__exact=recipient)
        except Account.DoesNotExist:
            account = None

        if account is None:
            raise forms.ValidationError("Account number is invalid")
        return recipient

    def save(self, commit=True):
        obj = super(LocalTxForms, self).save(commit=False)

        recipient = self.cleaned_data["receiver_acct_num"]
        amount = self.cleaned_data["amount"]
        purpose = self.cleaned_data["purpose"]
        dateCreated = self.cleaned_data["dateCreated"]
        receiver = Account.objects.get(username__exact=recipient)

        obj.sender = self.user
        obj.receiver = receiver
        obj.amount = amount
        obj.purpose = purpose
        obj.bank_name = "Onlineseacoast"
        obj.type = utils.TX_TYPE["LO"]
        obj.invoiceRef = utils.ref_code()
        obj.ben_acct = recipient
        obj.date = dateCreated

        # Save the object to the database if commit=True
        if commit:
            obj.save()

        return obj


class DomesticTxForms(forms.ModelForm):
    ben_account_number = forms.CharField(
        required=True,
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control",
                "placeholder": "Benneficiary account number",
            }
        ),
        label="Benneficiary Account No",
    )
    first_name = forms.CharField(
        required=True,
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control  ",
                "placeholder": "First name",
            }
        ),
        label="First Name",
    )
    last_name = forms.CharField(
        required=True,
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control  ",
                "placeholder": "Last name",
            }
        ),
        label="Last Name",
    )
    email = forms.EmailField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "type": "email",
                "class": "form-control  ",
                "placeholder": "Email",
            }
        ),
        label="Email",
    )

    route_num = forms.CharField(
        required=True,
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control  ",
                "placeholder": "ABA Routing No",
            }
        ),
        label="ABA Routing No",
    )
    bank_name = forms.CharField(
        required=True,
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control  ",
                "placeholder": "Bank Name",
            }
        ),
        label="Bank Name",
    )

    amount = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "type": "number",
                "class": "form-control  ",
                "placeholder": "Amount",
            }
        ),
        label="Amount",
    )
    purpose = forms.CharField(
        max_length=200,
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control form-control-lg",
                "placeholder": "brief description",
            }
        ),
        label="Purpose",
        required=True,
    )

    dateCreated = forms.DateTimeField(
        widget=forms.widgets.DateTimeInput(
            format="%Y-%m-%d %H:%M",
            attrs={
                "type": "datetime-local",
                "class": "form-control form-control-lg",
            },
        ),
        label="Date created",
        required=True,
    )

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
            "dateCreated",
        ]

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        obj = super(DomesticTxForms, self).save(commit=False)

        recipient = self.cleaned_data["ben_account_number"]
        amount = self.cleaned_data["amount"]
        purpose = self.cleaned_data["purpose"]
        dateCreated = self.cleaned_data["dateCreated"]

        details = InternationalDetails.objects.create(
            first_name=self.cleaned_data["first_name"],
            last_name=self.cleaned_data["last_name"],
            email=self.cleaned_data["email"],
        )

        obj.sender = self.user

        obj.amount = amount
        obj.purpose = purpose

        obj.type = utils.TX_TYPE["DO"]
        obj.invoiceRef = utils.ref_code()
        obj.ben_acct = recipient
        obj.bank_name = self.cleaned_data["bank_name"]
        obj.date = dateCreated

        obj.interDetail = details

        # Save the object to the database if commit=True
        if commit:
            obj.save()

        return obj


# international


class InterTxForms(forms.ModelForm):
    ben_account_number = forms.CharField(
        required=True,
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control",
                "placeholder": "Benneficiary account number",
            }
        ),
        label="Benneficiary Account No",
    )
    first_name = forms.CharField(
        required=True,
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control  ",
                "placeholder": "First name",
            }
        ),
        label="First Name",
    )
    last_name = forms.CharField(
        required=True,
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control  ",
                "placeholder": "Last name",
            }
        ),
        label="Last Name",
    )

    bank_name = forms.CharField(
        required=True,
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control  ",
                "placeholder": "Bank Name",
            }
        ),
        label="Bank Name",
    )

    amount = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "type": "number",
                "class": "form-control  ",
                "placeholder": "Amount",
            }
        ),
        label="Amount",
    )
    purpose = forms.CharField(
        max_length=200,
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control form-control-lg",
                "placeholder": "brief description",
            }
        ),
        label="Purpose",
        required=True,
    )

    swift_code = forms.CharField(
        max_length=50,
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control ",
                "placeholder": "Swift code",
            }
        ),
        label="Swift code",
        required=True,
    )

    iban_number = forms.CharField(
        max_length=50,
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control ",
                "placeholder": "Iban Number",
            }
        ),
        label="Iban Number",
        required=True,
    )

    city = forms.CharField(
        max_length=50,
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control ",
                "placeholder": "City",
            }
        ),
        label="City",
        required=True,
    )

    country = forms.CharField(
        max_length=50,
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control ",
                "placeholder": "Country",
            }
        ),
        label="Country",
        required=True,
    )

    dateCreated = forms.DateTimeField(
        widget=forms.widgets.DateTimeInput(
            format="%Y-%m-%d %H:%M",
            attrs={
                "type": "datetime-local",
                "class": "form-control form-control-lg",
            },
        ),
        label="Date created",
        required=True,
    )

    class Meta:
        model = Transactions
        fields = [
            "first_name",
            "last_name",
            "city",
            "country",
            "ben_account_number",
            "bank_name",
            "swift_code",
            "iban_number",
            "amount",
            "purpose",
            "dateCreated"
        ]

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        obj = super(InterTxForms, self).save(commit=False)

        recipient = self.cleaned_data["ben_account_number"]
        amount = self.cleaned_data["amount"]
        purpose = self.cleaned_data["purpose"]
        dateCreated = self.cleaned_data["dateCreated"]

        details = InternationalDetails.objects.create(
            first_name=self.cleaned_data["first_name"],
            last_name=self.cleaned_data["last_name"],
            country=self.cleaned_data["country"],
            city=self.cleaned_data["city"],
            iban_number=self.cleaned_data["iban_number"],
            bic_code=self.cleaned_data["swift_code"],
        )

        obj.sender = self.user

        obj.amount = amount
        obj.purpose = purpose
        obj.date = dateCreated

        obj.type = utils.TX_TYPE["IN"]
        obj.invoiceRef = utils.ref_code()
        obj.ben_acct = recipient
        obj.ban_name = self.cleaned_data["bank_name"]

        obj.interDetail = details

        # Save the object to the database if commit=True
        if commit:
            obj.save()
        return obj
