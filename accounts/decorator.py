from django.shortcuts import render
from functools import wraps

def role_required(allowed_roles=[]):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated and request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            return render(request, 'access_denied.html')  # Show Access Denied page
        return wrapped_view
    return decorator
