# registry/urls.py
# from django.urls import path, reverse_lazy
# from . import views
# from django.contrib.auth import views as auth_views  # Add this import

# app_name = 'registry'  # Namespace for your app



# urlpatterns = [
#     path('', views.index, name='home'),
#     path('register/', views.register, name='register'),
#     path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
#     path('record/<str:unique_id>/', views.view_record, name='view_record'),
#     path('export/', views.export_data, name='export_data'),
#     path('search/', views.search_records, name='search_records'),
#     path('signup/', views.signup, name='signup'),
#     path('register/success/<str:unique_id>/', views.registration_success, name='registration_success'),
    
#     # User routes
#     path('dashboard/', views.user_dashboard, name='user_dashboard'),
#     path('profile/edit/<int:parishioner_id>/', views.edit_profile, name='edit_profile'),
#     path('login/', views.user_login, name='login'),
#     path('verify-id/', views.verify_id, name='verify_id'),
    
#     # Admin routes
#     path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
#     path('admin/record/add/', views.add_record, name='add_record'),
#     path('admin/record/<str:unique_id>/edit/', views.edit_record, name='edit_record'),
#     path('admin/record/<str:unique_id>/delete/', views.delete_record, name='delete_record'),
    
#     # Add logout URL if not present
#     path('logout/', views.user_logout, name='logout'),
    
    
#     # Password reset URLs
#     path('password_reset/',
#          auth_views.PasswordResetView.as_view(
#              template_name='password_reset.html',  # Explicit path
#              email_template_name='email/password_reset_email.html',
#              subject_template_name='email/password_reset_subject.txt',
#              html_email_template_name='email/password_reset_email.html', 
#              extra_email_context={'site_name': 'Catholic Diocese of Enugu'}
#              success_url='registry:password_reset_complete'  # Add this line
            
#          ),
#          name='password_reset'),
    
#     path('password_reset/done/',
#          auth_views.PasswordResetDoneView.as_view(
#              template_name='password_reset_done.html'
#          ),
#          name='password_reset_done'),
    
#     path('reset/<uidb64>/<token>/',
#          auth_views.PasswordResetConfirmView.as_view(
#              template_name='password_reset_confirm.html',
#              post_reset_login=True,
#              post_reset_login_backend='django.contrib.auth.backends.ModelBackend',
#              success_url='registry:password_reset_complete'  # Add this line
#          ),
#          name='password_reset_confirm'),
    
#     path('reset/done/',
#          auth_views.PasswordResetCompleteView.as_view(
#              template_name='password_reset_complete.html'
#          ),
#          name='password_reset_complete'),
# ]


from django.urls import path, reverse_lazy
from . import views
from django.contrib.auth import views as auth_views

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
             extra_email_context={'site_name': 'Catholic Diocese of Enugu'},
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
    
    # Baptism
    path('submit-baptism/', views.submit_baptism, name='submit_baptism'),
    path('baptism-records/', views.baptism_records, name='baptism_records'),
    path('baptism/add/', views.add_baptism, name='add_baptism'),
    path('baptism/<int:baptism_id>/', views.view_baptism, name='view_baptism'),
    path('baptism/<int:baptism_id>/edit/', views.edit_baptism, name='edit_baptism'),
    path('baptism/<int:baptism_id>/delete/', views.delete_baptism, name='delete_baptism'),
]
