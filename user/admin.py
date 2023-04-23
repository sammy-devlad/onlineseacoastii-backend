from django.contrib import admin

from .models import Transactions, InternationalDetails

admin.site.register(Transactions)
admin.site.register(InternationalDetails)
