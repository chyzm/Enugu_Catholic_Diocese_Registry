# middleware.py
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin
from .models import Parish
from django.shortcuts import redirect
from django.urls import reverse


from django.http import HttpResponsePermanentRedirect

class DomainRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.get_host() == 'cderegistry.org.ng':
            return HttpResponsePermanentRedirect(f'https://cde.com.ng{request.get_full_path()}')
        
        return self.get_response(request)
 
         
class InitialSetupMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Skip middleware for static files, admin pages, and API endpoints
        if (request.path.startswith('/static/') or 
            request.path.startswith('/admin/') or  # Django admin
            request.path.startswith('/api/') or
            request.path.startswith('/media/')):  # Media files
            return self.get_response(request)
        
        # Skip if user is not authenticated
        if not request.user.is_authenticated:
            return self.get_response(request)
            
        # Skip if parishes already exist (setup completed)
        if Parish.objects.exists():
            return self.get_response(request)
            
        # Always allow superusers to navigate freely - no restrictions
        if request.user.is_superuser:
            return self.get_response(request)
            
        # For non-superusers when no parishes exist, you might want to show a message
        # or redirect to a "setup in progress" page, but for now let them navigate
        return self.get_response(request)
    
    

# class InitialSetupMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response
    
#     def __call__(self, request):
#         response = self.get_response(request)
        
#         # Skip for static files, Django admin URLs, API endpoints, and setup-related URLs
#         if (request.path.startswith('/static/') or 
#             request.path.startswith('/admin/') or  # Django admin
#             request.path.startswith('/api/') or
#             request.path == reverse('registry:initial_parish_setup') or
#             request.path.startswith('/admin-dashboard') or  # Your custom admin dashboard
#             request.path.startswith('/registry/admin/')):  # Your custom admin routes
#             return response
            
#         # Only redirect superuser to setup if no parishes exist and they're not already on admin pages
#         if (request.user.is_superuser and 
#             not Parish.objects.exists() and
#             not request.path.startswith('/admin/') and  # Django admin
#             not request.path.startswith('/admin-dashboard') and  # Your custom admin dashboard
#             not request.path.startswith('/registry/admin/') and  # Your custom admin routes
#             request.path != reverse('registry:initial_parish_setup')):
#             return redirect('registry:initial_parish_setup')
            
#         return response


