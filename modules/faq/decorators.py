from django.core.exceptions import PermissionDenied
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def is_faq_admin(user):
    return user.is_authenticated and user.is_staff


def faq_admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_staff:
            messages.error(request, 'Anda tidak memiliki akses untuk mengelola FAQ')
            return redirect('faq:faq_list')
        return view_func(request, *args, **kwargs)
    return _wrapped_view