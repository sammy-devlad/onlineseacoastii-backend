from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


User = get_user_model()

admin.site.unregister(Group)


class UserAdmin(BaseUserAdmin):
    list_display = ["email", "username"]
    list_filter = ["is_active"]
    fieldsets = (
        # (None, {"fields": ("email", "password")}),
        (
            ("Personal info"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "username",
                    "phone_number",
                    "date_of_birth",
                    "gender",
                    "next_of_kin",
                    "address",
                    "city",
                    "state",
                    "zipcode",
                    "country",
                    "account_type",
                    "security_pin",
                    "is_verified",
                )
            },
        ),
        (("Permissions"), {"fields": ("is_active", "is_staff", "is_superuser")}),
        (("Important dates"), {"fields": ("last_login", "date_joined")}),
        (
            ("Balance"),
            {"fields": ("balance",)},
        ),
    )

    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("first_name","last_name","security_pin","email", "password1", "password2")}),
    )
    search_fields = ["email"]
    ordering = ["email"]
    filter_horizontal = ()


admin.site.register(User, UserAdmin)
