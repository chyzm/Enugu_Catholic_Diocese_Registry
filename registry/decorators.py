from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect

# To ensure only admin access 

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('registry:login')
        if not (request.user.is_superuser or request.user.is_staff):
            return redirect('registry:user_dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper