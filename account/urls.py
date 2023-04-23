from django.urls import path
from .views import (
    SignUpView,
    ObtainAuthTokenView,
    ForgotPasswordAPIView,
    ResetPasswordAPIView,
    UserProfileImageUpdate,
)
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("sign-up/", SignUpView.as_view(), name="sign_up"),
    path("sign-in/", ObtainAuthTokenView.as_view(), name="sign_in"),
    path("create-new-account/", views.create_account, name="create_account"),
    path("forgot-password/", ForgotPasswordAPIView.as_view(), name="forgot_password"),
    path("reset-password/", ResetPasswordAPIView.as_view(), name="reset_password"),
    path(
        "change-profile/", UserProfileImageUpdate.as_view(), name="changeProfileImage"
    ),
]
