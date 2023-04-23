from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="admin-dashboard"),
    path("users/", views.users_, name="admin-users"),
    path("users/<int:pk>/", views.user_detail, name="admin-users-details"),
    path("transaction-logs/", views.transactions_, name="admin-transactions"),
    path(
        "transactions/<int:pk>/",
        views.transactions_details,
        name="admin-transactions_details",
    ),
    path("new-transaction/", views.create_transaction, name="admin-new-transactions"),
    path(
        "new-domestic-transaction/",
        views.create_transactionOB,
        name="admin-do-transactions",
    ),
    path(
        "new-international-transaction/",
        views.create_transactionIN,
        name="admin-in-transactions",
    ),
]
