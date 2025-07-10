from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import get_object_or_404, redirect
from functools import wraps
from django.http import HttpResponseForbidden
from .models import  Parishioner

# To ensure only admin access 

# decorators.py
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from functools import wraps
from django.http import HttpResponseForbidden

def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('registry:login')
        if not (request.user.is_superuser or request.user.is_staff or hasattr(request.user, 'priestprofile')):
            return redirect('registry:user_dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper

def priest_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('registry:login')
        if not (request.user.is_superuser or hasattr(request.user, 'priestprofile')):
            return redirect('registry:user_dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


def parish_admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('registry:login')
        if not (request.user.is_superuser or hasattr(request.user, 'parishadminprofile')):
            return redirect('registry:user_dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


# decorators.py



# ensure parish admins only see their parish data

# def parish_admin_required(view_func):
#     @wraps(view_func)
#     def _wrapped_view(request, *args, **kwargs):
#         if not request.user.is_authenticated:
#             return redirect('registry:login')
        
#         try:
#             parish_admin = request.user.parishadmin
#             # For views that deal with specific records, you can add:
#             if 'parishioner_id' in kwargs:
#                 parishioner = get_object_or_404(Parishioner, id=kwargs['parishioner_id'])
#                 if parishioner.parish != parish_admin.parish:
#                     return HttpResponseForbidden()
#         except ParishAdministrator.DoesNotExist:
#             return HttpResponseForbidden()
        
#         return view_func(request, *args, **kwargs)
#     return _wrapped_view