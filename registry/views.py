from django.shortcuts import render, redirect, get_object_or_404
from .models import Parishioner
from .forms import CustomUserCreationForm, ParishionerForm
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import csv
from registry import models
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import MultipleObjectsReturned
from django.contrib import messages  # Add this import at the top
from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator
from django.db.models import Count, Q, Case, When, Value, IntegerField
from django.db.models.functions import Concat
from django.urls import reverse
from urllib.parse import urlencode
from .decorators import admin_required



def index(request):
    return render(request, 'index.html')

# def register(request):
#     if request.method == 'POST':
#         parishioner = Parishioner(
#             title=request.POST.get('title', ''),
#             full_name=request.POST.get('full_name'),
#             email=request.POST.get('email'),
#             date_of_birth=request.POST.get('date_of_birth'),
#             gender=request.POST.get('gender'),
#             phone_number=request.POST.get('phone_number'),
#             marital_status=request.POST.get('marital_status', ''),
#             marriage_date=request.POST.get('marriage_date'),
#             marriage_details=request.POST.get('marriage_details', ''),
#             deceased=request.POST.get('deceased') == 'on',
#             date_of_death=request.POST.get('date_of_death'),
#             death_details=request.POST.get('death_details', ''),
#             parish=request.POST.get('parish'),
#             deanery=request.POST.get('deanery'),
#             station=request.POST.get('station'),
#             baptized=request.POST.get('baptized') == 'on',
#             confirmed=request.POST.get('confirmed') == 'on',
#             first_communion=request.POST.get('first_communion') == 'on',
#             education_level=request.POST.get('education_level', ''),
#             occupation=request.POST.get('occupation', ''),
#             employment_status=request.POST.get('employment_status', ''),
#         )
#         parishioner.save()
        
#         # Send email if email is provided
#         email_sent = False
#         if parishioner.email:
#             email_sent = send_registration_email(parishioner)
        
#         return render(request, 'registration-success-page.html', {
#             'unique_id': parishioner.unique_id,
#             'parishioner': parishioner,  # Pass the parishioner object
#             'email_sent': email_sent  # Pass whether email was sent
#         })
#     return render(request, 'register.html')


from django.core.exceptions import ValidationError
from django.utils.dateparse import parse_date

def register(request):
    if request.method == 'POST':
        try:
            # Parse and validate date fields
            date_of_birth = request.POST.get('date_of_birth')
            if not date_of_birth:
                raise ValidationError("Date of birth is required")
            
            dob = parse_date(date_of_birth)
            if dob is None:
                raise ValidationError("Invalid date format for date of birth. Use YYYY-MM-DD")
            
            # Handle optional dates
            marriage_date = request.POST.get('marriage_date')
            md = parse_date(marriage_date) if marriage_date else None
            
            date_of_death = request.POST.get('date_of_death')
            dod = parse_date(date_of_death) if date_of_death else None
            
            email = request.POST.get('email')
            if email and Parishioner.objects.filter(email__iexact=email).exists():
                return render(request, 'register.html', {
                    'error': 'This email is already registered',
                    'form_data': request.POST
                })
            
            
            
            parishioner = Parishioner(
                # title=request.POST.get('title', ''),
                # full_name=request.POST.get('full_name'),
                # email=request.POST.get('email'),
                
                title=request.POST.get('title', ''),
                full_name=request.POST.get('full_name'),
                email=email,
                date_of_birth=dob,
                gender=request.POST.get('gender'),
                phone_number=request.POST.get('phone_number'),
                marital_status=request.POST.get('marital_status', ''),
                marriage_date=md,
                marriage_details=request.POST.get('marriage_details', ''),
                deceased=request.POST.get('deceased') == 'on',
                date_of_death=dod,
                death_details=request.POST.get('death_details', ''),
                parish=request.POST.get('parish'),
                deanery=request.POST.get('deanery'),
                station=request.POST.get('station'),
                baptized=request.POST.get('baptized') == 'on',
                confirmed=request.POST.get('confirmed') == 'on',
                first_communion=request.POST.get('first_communion') == 'on',
                education_level=request.POST.get('education_level', ''),
                occupation=request.POST.get('occupation', ''),
                employment_status=request.POST.get('employment_status', ''),
            )
            parishioner.save()
            
            # Send email if email is provided
            email_sent = False
            if parishioner.email:
                email_sent = send_registration_email(parishioner)
            
            return render(request, 'registration-success-page.html', {
                'unique_id': parishioner.unique_id,
                'parishioner': parishioner,
                'email_sent': email_sent
            })
            
        except ValidationError as e:
            return render(request, 'register.html', {
                'error': str(e),
                'form_data': request.POST  # Pass back form data to repopulate form
            })
        except Exception as e:
            return render(request, 'register.html', {
                'error': f"An error occurred: {str(e)}",
                'form_data': request.POST
            })
    
    return render(request, 'register.html')



def send_registration_email(parishioner):
    if not parishioner.email:
        return False
        
    subject = 'Catholic Diocese of Enugu - Registration Confirmation'
    html_message = render_to_string('email/registration_confirmation.html', {  # Remove 'email/' if not in subfolder
        'parishioner': parishioner,
        'unique_id': parishioner.unique_id
    })
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [parishioner.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False
    
    
    



def admin_check(user):
    return user.is_authenticated and (user.is_superuser or user.is_staff)

@user_passes_test(admin_check, login_url='registry:login')
def admin_dashboard(request):
    # Get filter parameters
    search_query = request.GET.get('q', '')
    deanery_filter = request.GET.get('deanery', '')
    status_filter = request.GET.get('status', '')
    
    # Build query
    parishioners = Parishioner.objects.all()
    
    if search_query:
        parishioners = parishioners.filter(
            Q(full_name__icontains=search_query) |
            Q(unique_id__icontains=search_query) |
            Q(parish__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone_number__icontains=search_query)
        )
    
    if deanery_filter:
        parishioners = parishioners.filter(deanery=deanery_filter)
    
    if status_filter:
        if status_filter == 'baptized':
            parishioners = parishioners.filter(baptized=True)
        elif status_filter == 'confirmed':
            parishioners = parishioners.filter(confirmed=True)
        elif status_filter == 'deceased':
            parishioners = parishioners.filter(deceased=True)
    
    # Order by most recent first
    parishioners = parishioners.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(parishioners, 25)  # Show 25 records per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Calculate stats
    total_parishioners = Parishioner.objects.count()
    baptized_count = Parishioner.objects.filter(baptized=True).count()
    confirmed_count = Parishioner.objects.filter(confirmed=True).count()
    deceased_count = Parishioner.objects.filter(deceased=True).count()
    
    stats = {
        'total_parishioners': total_parishioners,
        'baptized_count': baptized_count,
        'confirmed_count': confirmed_count,
        'deceased_count': deceased_count,
        'baptized_percentage': round((baptized_count / total_parishioners * 100) if total_parishioners > 0 else 0, 1),
        'confirmed_percentage': round((confirmed_count / total_parishioners * 100) if total_parishioners > 0 else 0, 1),
    }
    
    # Preserve query parameters for pagination
    query_params = request.GET.copy()
    if 'page' in query_params:
        del query_params['page']
    query_params = query_params.urlencode()
    
    return render(request, 'admin/admin_dashboard.html', {
        'parishioners': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'query_params': query_params,
        'stats': stats,
        'deanery_choices': Parishioner.DEANERY_CHOICES,
    })

@user_passes_test(admin_check, login_url='registry:login')
def add_record(request):
    if not request.user.is_superuser:
        return redirect('registry:admin_dashboard')
    
    if request.method == 'POST':
        form = ParishionerForm(request.POST)
        if form.is_valid():
            parishioner = form.save(commit=False)
            parishioner.created_by = request.user
            parishioner.save()
            messages.success(request, 'Record added successfully!')
            return redirect('registry:view_record', unique_id=parishioner.unique_id)
    else:
        form = ParishionerForm()
    
    return render(request, 'admin/add_record.html', {'form': form})

@user_passes_test(admin_check, login_url='registry:login')
def edit_record(request, unique_id):
    parishioner = get_object_or_404(Parishioner, unique_id=unique_id)
    
    if request.method == 'POST':
        form = ParishionerForm(request.POST, instance=parishioner)
        if form.is_valid():
            form.save()
            messages.success(request, 'Record updated successfully!')
            return redirect('registry:view_record', unique_id=parishioner.unique_id)
    else:
        form = ParishionerForm(instance=parishioner)
    
    return render(request, 'admin/edit_record.html', {
        'form': form,
        'parishioner': parishioner
    })

@user_passes_test(lambda u: u.is_superuser, login_url='registry:login')
def delete_record(request, unique_id):
    parishioner = get_object_or_404(Parishioner, unique_id=unique_id)
    
    if request.method == 'POST':
        parishioner.delete()
        messages.success(request, 'Record deleted successfully!')
        return redirect('registry:admin_dashboard')
    
    return render(request, 'admin/confirm_delete.html', {'parishioner': parishioner})

def view_record(request, unique_id):
    parishioner = get_object_or_404(Parishioner, unique_id=unique_id)
    return render(request, 'admin/view_record.html', {'parishioner': parishioner})

def export_data(request):
    if not request.user.is_staff:
        return redirect('home')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="parishioners.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'ID', 'Name', 'Email', 'Date of Birth', 'Gender', 'Parish', 'Deanery', 
        'Station', 'Baptized', 'Confirmed', 'First Communion', 'Education Level',
        'Occupation', 'Employment Status'
    ])
    
    for parishioner in Parishioner.objects.all():
        writer.writerow([
            parishioner.unique_id,
            parishioner.full_name,
            parishioner.email,
            parishioner.date_of_birth,
            parishioner.get_gender_display(),
            parishioner.parish,
            parishioner.deanery,
            parishioner.station,
            'Yes' if parishioner.baptized else 'No',
            'Yes' if parishioner.confirmed else 'No',
            'Yes' if parishioner.first_communion else 'No',
            parishioner.get_education_level_display() if parishioner.education_level else 'N/A',
            parishioner.occupation if parishioner.occupation else 'N/A',
            parishioner.get_employment_status_display() if parishioner.employment_status else 'N/A',
        ])
    
    return response

def search_records(request):
    query = request.GET.get('q', '')
    results = Parishioner.objects.filter(
        models.Q(full_name__icontains=query) |
        models.Q(unique_id__icontains=query) |
        models.Q(parish__icontains=query) |
        models.Q(email__icontains=query)
    )
    return render(request, 'search_results.html', {'results': results, 'query': query})

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        unique_id = request.POST.get('unique_id', '').strip().upper()
        email = request.POST.get('email', '').strip().lower()
        
        # First verify the parishioner record exists with matching email and ID
        try:
            parishioner = Parishioner.objects.get(
                unique_id__iexact=unique_id,
                email__iexact=email
            )
        except Parishioner.DoesNotExist:
            # Check if ID exists but email doesn't match
            if Parishioner.objects.filter(unique_id__iexact=unique_id).exists():
                return render(request, 'signup.html', {
                    'form': form,
                    'error': 'Email does not match the one in our records for this ID'
                })
            return render(request, 'signup.html', {
                'form': form,
                'error': 'No parishioner record found with this ID and email combination'
            })
        
        if form.is_valid():
            user = form.save()
            login(request, user)
            
            # Automatically link the parishioner record to the user
            request.session['verified_parishioner_id'] = parishioner.id
            return redirect('registry:user_dashboard')
        
    else:
        initial = {}
        if 'email' in request.GET:
            initial['email'] = request.GET['email']
        form = CustomUserCreationForm(initial=initial)
    
    return render(request, 'signup.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            auth_login(request, user)
            
            # Check if already verified
            if 'verified_parishioner_id' in request.session:
                return redirect('registry:user_dashboard')
                
            # Render login template with verification form
            return render(request, 'login.html', {
                'user': request.user,
                'show_verification': True
            })
        else:
            return render(request, 'login.html', {
                'error': 'Invalid username or password'
            })
    
    return render(request, 'login.html')


from django.contrib.auth import logout as auth_logout
from django.shortcuts import redirect

def user_logout(request):
    """Handle user logout and clear session data"""
    # Clear verification session data
    if 'verified_parishioner_id' in request.session:
        del request.session['verified_parishioner_id']
    
    # Perform Django's built-in logout
    auth_logout(request)
    
    # Redirect to home page
    return redirect('registry:home')



@login_required
def verify_id(request):
    if request.method == 'POST':
        unique_id = request.POST.get('unique_id', '').strip().upper()
        user_email = request.user.email.lower()
        
        print(f"Verification attempt - ID: {unique_id}, Email: {user_email}")  # Debug
        
        try:
            parishioner = Parishioner.objects.get(
                unique_id__iexact=unique_id,
                email__iexact=user_email
            )
            
            # Store verification in session
            request.session['verified_parishioner_id'] = parishioner.id
            request.session['verified_parishioner_name'] = parishioner.full_name
            
            # Force session save
            request.session.modified = True
            print(f"Session after verification: {request.session.items()}")  # Debug
            
            # Verify session saved properly
            from django.contrib.sessions.backends.db import SessionStore
            session_key = request.session.session_key
            print(f"Session key: {session_key}")
            
            return redirect('registry:user_dashboard')
            
        except Parishioner.DoesNotExist:
            error_msg = 'No matching parishioner record found'
            if Parishioner.objects.filter(unique_id__iexact=unique_id).exists():
                error_msg = 'Email does not match our records for this ID'
            return render(request, 'login.html', {
                'user': request.user,
                'show_verification': True,
                'verification_error': error_msg
            })
            
        except Exception as e:
            print(f"Verification error: {str(e)}")  # Debug
            return render(request, 'login.html', {
                'user': request.user,
                'show_verification': True,
                'verification_error': 'An error occurred during verification'
            })
    
    return redirect('registry:login')



@login_required
def user_dashboard(request):
    print(f"Dashboard access attempt - Session: {request.session.items()}")  # Debug
    
    # Check verification
    if 'verified_parishioner_id' not in request.session:
        print("No verification in session - redirecting")  # Debug
        return redirect('registry:verify_id')
    
    try:
        parishioner = Parishioner.objects.get(
            id=request.session['verified_parishioner_id'],
            email__iexact=request.user.email
        )
        print(f"Showing dashboard for {parishioner.full_name}")  # Debug
        return render(request, 'user_dashboard.html', {
            'parishioner': parishioner
        })
        
    except Parishioner.DoesNotExist:
        print("Parishioner not found - clearing session")  # Debug
        if 'verified_parishioner_id' in request.session:
            del request.session['verified_parishioner_id']
        return redirect('registry:verify_id')
    except Exception as e:
        print(f"Dashboard error: {str(e)}")  # Debug
        return redirect('registry:verify_id')

# @login_required
# def user_dashboard(request):
#     if 'verified_parishioner_id' not in request.session:
#         return redirect('registry:verify_id')
    
#     try:
#         parishioner = Parishioner.objects.get(id=request.session['verified_parishioner_id'])
#         return render(request, 'user_dashboard.html', {'parishioner': parishioner})
#     except (Parishioner.DoesNotExist, MultipleObjectsReturned):
#         del request.session['verified_parishioner_id']
#         return redirect('registry:verify_id')
    
from django.contrib import messages  # Add this import at the top

@login_required
def edit_profile(request, parishioner_id):
    # Get the parishioner or return 404
    parishioner = get_object_or_404(Parishioner, id=parishioner_id)
    
    # Ensure the user can only edit their own profile
    if not (request.user.is_staff or parishioner.email == request.user.email):
        return redirect('registry:user_dashboard')
    
    if request.method == 'POST':
        form = ParishionerForm(request.POST, instance=parishioner)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('registry:user_dashboard')
    else:
        form = ParishionerForm(instance=parishioner)
    
    return render(request, 'edit_profile.html', {
        'form': form,
        'parishioner': parishioner
    })
    
    
    

def registration_success(request, unique_id):
    return render(request, 'registration-success-page.html', {
        'unique_id': unique_id,
        'email': request.POST.get('email', '')
    })
    
    
    
    