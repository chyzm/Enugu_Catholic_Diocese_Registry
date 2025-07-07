from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin
from .models import SubAdminProfile

class SubAdminFilterMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated and request.user.is_subadmin:
            try:
                profile = request.user.subadmin_profile
                request.parish_filter = {'parish': profile.parish}
            except SubAdminProfile.DoesNotExist:
                pass
        return None
    
    

# registry/middleware.py
from django.shortcuts import redirect

class AuthRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.user.is_authenticated:
            if request.path == reverse('registry:login'):
                if request.user.is_subadmin:
                    return redirect('registry:subadmin_dashboard')
                return redirect('registry:user_dashboard')
        return None