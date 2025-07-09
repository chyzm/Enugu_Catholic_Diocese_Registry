from django.contrib import admin
from django.urls import include, path
from registry import views
from django.contrib.auth.views import LoginView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='home'),
    path('record/<str:unique_id>/', views.view_record, name='view_record'),
    path('registry/', include('registry.urls')),
    path('accounts/login/', LoginView.as_view(template_name='login.html'), name='login'),
]

# ✅ Add this for dev static files
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
