from django.urls import path
from . import views


urlpatterns = [
    path("transactions/", views.user_transactions, name="transaction"),
    path("transactions/<int:pk>", views.transaction_detail, name="transaction_detail"),
    path("dashboard/", views.dashboard, name="transaction"),
    path("validate-account-numbers/", views.get_ben_name, name="get_ben_name"),
    path("transfer-same/", views.transferSb, name="transfer-same"),
    path("transfer-others/", views.transferOb, name="transfer-ob"),
    path("transfer-inter/", views.transferIn, name="transfer-in"),
    path("reset-support-pin/", views.resetPin, name="resetPin"),
]
