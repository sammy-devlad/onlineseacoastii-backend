from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import (
    CreateAcctSerializer,
    ProfileSerializer,
    RegisterSerializer,
    UpdateProfileImgSerializer,
)
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated

from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import EmailMessage
from django.template.loader import get_template
from django.utils.encoding import force_str
from rest_framework import generics, permissions
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from django.http import HttpResponseRedirect

from django.core.cache import cache
from account.models import Account


from baseapp import utils


def home(request):
    return HttpResponseRedirect("https://app.onlineseacoastacct.com/")


class SignUpView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, format=None):
        uidb64 = request.GET.get("authToken")
        if uidb64:
            ke_y = force_str(urlsafe_base64_decode(uidb64))
            data = cache.get(ke_y)
            if data:
                return JsonResponse(data)
            else:
                return JsonResponse({"error": "Link is invalid!"})
        else:
            return JsonResponse({"error": "Link is invalid"})

    def post(self, request, format=None):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            current_site = get_current_site(request)
            subject = f"welcome to onlineseacoast, confirm your email address"
            user = {
                "email": serializer.data["email"],
                "password": serializer.data["password"],
            }
            ke_y = cache.get(user["email"])
            if ke_y:
                cache.delete(user["email"])
            cache.set(user["email"], user, timeout=300)
            context = {
                "user": user,
                "domain": current_site.domain,
                "token": urlsafe_base64_encode(force_bytes(user["email"])),
            }
            message = get_template("account/confirmation.email.html").render(context)
            mail = EmailMessage(
                subject=subject,
                body=message,
                from_email=utils.EMAIL_ADMIN,
                to=[user["email"]],
                reply_to=[utils.EMAIL_ADMIN],
            )
            mail.content_subtype = "html"
            mail.send(fail_silently=True)

            return Response({"msg": "Successful"})
        else:
            return Response(serializer.errors)


@api_view(["POST"])
@permission_classes([AllowAny])
def create_account(request):
    # print("Recieving request")
    serializer = CreateAcctSerializer(data=request.data)
    if serializer.is_valid():
        instance = serializer.save()
        cache.delete(serializer.data["email"])
        current_site = get_current_site(request)
        subject = f"Welcome to {current_site.domain}"
        context = {
            "user": instance,
            "domain": current_site.domain,
        }
        message = get_template("account/welcome.email.html").render(context)
        mail = EmailMessage(
            subject=subject,
            body=message,
            from_email=utils.EMAIL_ADMIN,
            to=[instance.email],
            reply_to=[utils.EMAIL_ADMIN],
        )
        mail.content_subtype = "html"
        mail.send(fail_silently=True)

        return Response({"msg": "Successful"})
    else:
        print(serializer.errors)
        return Response(serializer.errors)


class ObtainAuthTokenView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        context = {}

        username = request.data.get("username")
        password = request.data.get("password")
        # print(username, password)
        account = authenticate(request, username=username, password=password)
        if account:
            try:
                token = Token.objects.get(user=account)
            except Token.DoesNotExist:
                token = Token.objects.create(user=account)
            serializer = ProfileSerializer(account)
            context["msg"] = "Successfully authenticated."
            context["user"] = serializer.data
            context["token"] = token.key
        else:
            context["error"] = "Invalid username or password"

        return Response(context)


class ForgotPasswordAPIView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, format=None):
        res = {}
        # print(request.data)
        email = request.data.get("email", "0")
        # print("email is", email)
        user = None
        try:
            user = Account.objects.get(email__exact=email)
            print(user)
        except:
            print("Not found")
            res["error"] = "Email not found"

        if user:
            current_site = get_current_site(request)
            subject = f"Reset password {current_site.domain}"
            context = {
                "user": user,
                "domain": current_site.domain,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": default_token_generator.make_token(user),
            }
            message = get_template("account/resetPassword.html").render(context)
            mail = EmailMessage(
                subject=subject,
                body=message,
                from_email=utils.EMAIL_ADMIN,
                to=[user.email],
                reply_to=[utils.EMAIL_ADMIN],
            )
            mail.content_subtype = "html"
            mail.send(fail_silently=True)
            res["msg"] = "SUCCESS"

        return Response(res)


class ResetPasswordAPIView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, format=None):
        newpassword = request.data.get("newpassword")
        confirmpassword = request.data.get("confirmnewpassword")
        pk = int(request.data.get("id"))
        print(newpassword, confirmpassword)

        if newpassword != confirmpassword:
            return Response({"error": True, "msg": "Password dont match"})

        try:
            user = Account.objects.get(pk=pk)
        except Account.DoesNotExist:
            user = None

        if user is not None:
            user.set_password(newpassword)
            user.save()
            return Response({"error": False, "msg": "Password safed"})
        return Response({"error": True, "msg": "User not found"})

    def get(self, request, format=None):
        uidb64 = request.GET.get("uid")
        token = request.GET.get("token")
        context = {}

        if token and uidb64:
            try:
                uid = force_str(urlsafe_base64_decode(uidb64))
                user = Account.objects.get(pk=uid)
            except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
                user = None

            if user is not None and default_token_generator.check_token(user, token):
                context["user"] = {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                }
                context["error"] = False

                return Response(context)
            else:
                context["error"] = True
                return Response(context)

        else:
            context["error"] = True
            return Response(context)


class UserProfileImageUpdate(generics.UpdateAPIView):
    parser_classes = (
        MultiPartParser,
        FormParser,
    )
    permission_classes = (permissions.IsAuthenticated,)

    def put(self, request, format=None):
        serializer = UpdateProfileImgSerializer(
            request.user,
            data=request.data,
        )
        if serializer.is_valid():
            instance = serializer.save()
            profile = ProfileSerializer(instance)

            return Response({"user": profile.data})
        else:
            print(serializer.errors)
            return Response({"error": True}, status=400)
