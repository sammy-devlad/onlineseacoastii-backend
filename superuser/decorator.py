from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test


def superuser_required(
    function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url="/admin/login/"
):
    actual_decorator = user_passes_test(
        lambda u: u.is_staff or u.is_superuser,
        login_url=login_url,
        redirect_field_name=redirect_field_name,
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
