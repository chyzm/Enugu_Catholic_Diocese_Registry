
from django.urls import path, reverse_lazy
from . import views
from django.contrib.auth import views as auth_views
# from .views import get_parishioner_by_id
# from .views import get_parishioner_by_unique_id


app_name = 'registry'

urlpatterns = [
    path('', views.index, name='home'),
    path('register/', views.register, name='register'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('record/<str:unique_id>/', views.view_record, name='view_record'),
    path('export/', views.export_data, name='export_data'),
    path('search/', views.search_records, name='search_records'),
    path('signup/', views.signup, name='signup'),
    path('register/success/<str:unique_id>/', views.registration_success, name='registration_success'),

    # User routes
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('profile/edit/<int:parishioner_id>/', views.edit_profile, name='edit_profile'),
    path('login/', views.user_login, name='login'),
    path('verify-id/', views.verify_id, name='verify_id'),

    # Admin routes
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/record/add/', views.add_record, name='add_record'),
    path('admin/record/<str:unique_id>/edit/', views.edit_record, name='edit_record'),
    path('admin/record/<str:unique_id>/delete/', views.delete_record, name='delete_record'),

    # Logout route
    path('logout/', views.user_logout, name='logout'),

    # Password reset URLs
    path('password_reset/',
         auth_views.PasswordResetView.as_view(
             template_name='password_reset.html',
             email_template_name='email/password_reset_email.html',
             subject_template_name='email/password_reset_subject.txt',
             html_email_template_name='email/password_reset_email.html',
             extra_email_context={'site_name': 'Catholic Diocese of Enugu Registry'},
             success_url=reverse_lazy('registry:password_reset_done')
         ),
         name='password_reset'),

    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='password_reset_done.html'
         ),
         name='password_reset_done'),

    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='password_reset_confirm.html',
             post_reset_login=True,
             post_reset_login_backend='django.contrib.auth.backends.ModelBackend',
             success_url=reverse_lazy('registry:password_reset_complete')
         ),
         name='password_reset_confirm'),

    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='password_reset_complete.html'
         ),
         name='password_reset_complete'),
    
    # Birth record
    path('submit-birth-record/', views.submit_birth_record, name='submit_birth_record'),  # Changed from submit_baptism
    path('birth-records/', views.birth_records, name='birth_records'),  # Changed from baptism_records
    path('birth/add/', views.add_birth_record, name='add_birth_record'),  # Changed from add_baptism
    path('birth/<int:birth_record_id>/', views.view_birth_record, name='view_birth_record'),  # Changed from view_baptism
    path('birth/<int:birth_record_id>/edit/', views.edit_birth_record, name='edit_birth_record'),  # Changed from edit_baptism
    path('birth/<int:birth_record_id>/delete/', views.delete_birth_record, name='delete_birth_record'),  # Changed from delete_baptism
    
    # Assign priest
    path('admin/assign-priest/', views.assign_priest, name='assign_priest'),
    
    # Assign Parish Admin
    path('admin/assign-admin/', views.assign_admin, name='assign_admin'),
    
    # Privacy
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    
    # Terms
    path('terms-and-conditions/', views.terms_and_conditions, name='terms_and_conditions'),
    
   
]

