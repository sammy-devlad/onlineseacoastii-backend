import random
from django.conf import settings
from django.utils import timezone
from uuid import uuid4

from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import get_template


def gen_random_number():
    return str(random.randint(1000000000, 9999999999))


EMAIL_ADMIN = settings.DEFAULT_FROM_EMAIL
D = "deposite"
W = "withdraw"


def get_next_destination(request):
    next = None
    if request.GET.get("next"):
        next = str(request.GET.get("next"))
    return next


def ref_code():
    code = str(uuid4()).replace(" ", "-").upper()[:8]
    return code


STATUS = {
    "PENDING": "PENDING",
    "SUCCESS": "SUCCESS",
    "DECLINED": "DECLINED",
}

TX_TYPE = {"LO": "Local transfer", "DO": "Domestic transfer", "IN": "International"}


def alertTx(transaction, current_site, subject, status, to_email, name):
    context = {
        "name": name,
        "domain": current_site.domain,
        "tx": transaction,
        "ty_pe": status,
    }
    message = get_template("superuser/txprocess.email.html").render(context)
    mail = EmailMessage(
        subject=subject,
        body=message,
        from_email=EMAIL_ADMIN,
        to=[to_email],
        reply_to=[EMAIL_ADMIN],
    )
    mail.content_subtype = "html"
    mail.send(fail_silently=True)
