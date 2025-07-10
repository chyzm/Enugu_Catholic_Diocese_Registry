import datetime
from time import timezone
from django.shortcuts import render, redirect, get_object_or_404
from .models import BirthRecord, Deanery, Parish, Parishioner
from .forms import BirthRecordForm, CustomUserCreationForm, ParishionerForm
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
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
import random
import string
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
import json

from .models import Parishioner, PriestProfile, ParishAdminProfile
from .forms import PriestAssignmentForm, AdminAssignmentForm


def generate_verification_code(length=6):
    """Generate a random numeric verification code"""
    return ''.join(random.choices(string.digits, k=length))



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



from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings


def send_registration_email(parishioner):
    if not parishioner.email:
        print("No email address found for parishioner.")
        return False

    subject = 'Catholic Diocese of Enugu - Registration Confirmation'

    # Render the email content
    html_message = render_to_string('email/registration_confirmation.html', {
        'parishioner': parishioner,
        'unique_id': parishioner.unique_id
    })
    plain_message = strip_tags(html_message)

    sender_email = settings.DEFAULT_FROM_EMAIL
    recipient_email = parishioner.email

    print(f"Sending email from: {sender_email}")
    print(f"Sending email to: {recipient_email}")

    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=sender_email,
            recipient_list=[recipient_email],
            html_message=html_message,
            fail_silently=False,
        )
        print("Email sent successfully.")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False
    
    


def admin_check(user):
    return user.is_authenticated and (user.is_superuser or user.is_staff or hasattr(user, 'priestprofile'))







def get_user_parish(user):
    if hasattr(user, 'priestprofile'):
        return user.priestprofile.parish
    elif hasattr(user, 'parishadminprofile'):
        return user.parishadminprofile.parish
    return None

# views.py
from django.contrib.auth.models import User, Group
from .models import Parishioner, Parish, PriestProfile, ParishAdminProfile


@user_passes_test(lambda u: u.is_superuser or u.is_staff)
def admin_dashboard(request):
    # Initialize variables
    parishioners = Parishioner.objects.none()  # Default empty queryset
    parishes = Parish.objects.none()  # Default empty queryset
    
    # Get available parishioners for role assignment
       # Get available parishioners for role assignment - filter by parish
    if request.user.is_superuser:
        available_parishioners = Parishioner.objects.all().order_by('full_name')
        parishes = Parish.objects.all()
        parishioners = Parishioner.objects.all()
    elif hasattr(request.user, 'priestprofile'):
        parish = request.user.priestprofile.parish
        parishes = Parish.objects.filter(id=parish.id)
        parishioners = Parishioner.objects.filter(parish=parish.name)
        available_parishioners = Parishioner.objects.filter(parish=parish.name).order_by('full_name')
    elif hasattr(request.user, 'parishadminprofile'):
        parish = request.user.parishadminprofile.parish
        parishes = Parish.objects.filter(id=parish.id)
        parishioners = Parishioner.objects.filter(parish=parish.name)
        available_parishioners = Parishioner.objects.filter(parish=parish.name).order_by('full_name')
    
    # Get filter parameters
    search_query = request.GET.get('q', '')
    deanery_filter = request.GET.get('deanery', '')
    status_filter = request.GET.get('status', '')
    
    # Apply filters
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
    paginator = Paginator(parishioners, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    
    # Map
    features = [
        {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [p.longitude, p.latitude]
            },
            "properties": {
                "unique_id": p.unique_id,
                "parish": p.parish,
            }
        }
        for p in parishioners if p.latitude and p.longitude
    ]

    geojson = {
        "type": "FeatureCollection",
        "features": features
    }
    
    # Calculate stats - ensure we use the filtered queryset
    total_parishioners = parishioners.count()
    baptized_count = parishioners.filter(baptized=True).count()
    confirmed_count = parishioners.filter(confirmed=True).count()
    deceased_count = parishioners.filter(deceased=True).count()
    
    stats = {
        'total_parishioners': total_parishioners,
        'baptized_count': baptized_count,
        'confirmed_count': confirmed_count,
        'deceased_count': deceased_count,
        'baptized_percentage': round((baptized_count / total_parishioners * 100) if total_parishioners > 0 else 0),
        'confirmed_percentage': round((confirmed_count / total_parishioners * 100) if total_parishioners > 0 else 0),
    }
    
    # Preserve query parameters for pagination
    query_params = request.GET.copy()
    if 'page' in query_params:
        del query_params['page']
    query_params = query_params.urlencode()
    
    return render(request, 'admin/admin_dashboard.html', {
        'available_parishioners': available_parishioners,
        'parishes': parishes,
        'parishioners': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'query_params': query_params,
        'stats': stats,
        'deanery_choices': Parishioner.DEANERY_CHOICES,
        'geojson_data': json.dumps(geojson),
    })
    
    
    
@user_passes_test(lambda u: u.is_superuser)
def assign_priest(request):
    if request.method == "POST":
        parishioner_id = request.POST.get('parishioner_id')
        parish_id = request.POST.get('parish_id')
        
        
        
          # Check if superuser or if parish belongs to the user
        if not request.user.is_superuser:
            if hasattr(request.user, 'priestprofile'):
                if int(parish_id) != request.user.priestprofile.parish.id:
                    messages.error(request, "You can only assign priests to your own parish")
                    return redirect('registry:admin_dashboard')
            elif hasattr(request.user, 'parishadminprofile'):
                if int(parish_id) != request.user.parishadminprofile.parish.id:
                    messages.error(request, "You can only assign priests to your own parish")
                    return redirect('registry:admin_dashboard')
        
        try:
            parishioner = Parishioner.objects.get(id=parishioner_id)
            parish = Parish.objects.get(id=parish_id)
            
            # Create or get user account
            user, created = User.objects.get_or_create(
                email=parishioner.email,
                defaults={
                    'username': parishioner.email.split('@')[0],
                    'first_name': parishioner.full_name.split()[0],
                    'last_name': ' '.join(parishioner.full_name.split()[1:]),
                    'is_staff': True
                }
            )
            
            if not created:
                user.is_staff = True
                user.save()
            
            # Create priest profile
            PriestProfile.objects.get_or_create(
                user=user,
                parish=parish,
                created_by=request.user
            )
            
            # Add to priest group
            group, _ = Group.objects.get_or_create(name='Priest')
            user.groups.add(group)
            
            messages.success(request, f"{parishioner.full_name} assigned as priest to {parish.name}")
        except Exception as e:
            messages.error(request, f"Error assigning priest: {str(e)}")
    
    return redirect('registry:admin_dashboard')



# @user_passes_test(lambda u: u.is_superuser or u.is_staff)
@user_passes_test(lambda u: u.is_superuser or hasattr(u, 'priestprofile'))
def assign_admin(request):
    if request.method == "POST":
        parishioner_id = request.POST.get('parishioner_id')
        parish_id = request.POST.get('parish_id')
        
        
        # Check if superuser or if parish belongs to the user
        if not request.user.is_superuser:
            if hasattr(request.user, 'priestprofile'):
                if int(parish_id) != request.user.priestprofile.parish.id:
                    messages.error(request, "You can only assign admins to your own parish")
                    return redirect('registry:admin_dashboard')
            elif hasattr(request.user, 'parishadminprofile'):
                if int(parish_id) != request.user.parishadminprofile.parish.id:
                    messages.error(request, "You can only assign admins to your own parish")
                    return redirect('registry:admin_dashboard')
        
        try:
            parishioner = Parishioner.objects.get(id=parishioner_id)
            parish = Parish.objects.get(id=parish_id)
            
            # Create or get user account
            user, created = User.objects.get_or_create(
                email=parishioner.email,
                defaults={
                    'username': parishioner.email.split('@')[0],
                    'first_name': parishioner.full_name.split()[0],
                    'last_name': ' '.join(parishioner.full_name.split()[1:]),
                    'is_staff': True
                }
            )
            
            if not created:
                user.is_staff = True
                user.save()
            
            # Create parish admin profile
            ParishAdminProfile.objects.get_or_create(
                user=user,
                parish=parish,
                created_by=request.user
            )
            
            # Add to parish admin group
            group, _ = Group.objects.get_or_create(name='Parish Admin')
            user.groups.add(group)
            
            messages.success(request, f"{parishioner.full_name} assigned as admin to {parish.name}")
        except Exception as e:
            messages.error(request, f"Error assigning admin: {str(e)}")
    
    return redirect('registry:admin_dashboard')



# Privacy policy view
def privacy_policy(request):
    return render(request, 'privacy.html')


# Terms and Condition view
def terms_and_conditions(request):
    return render(request, 'terms.html')
    



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


# SEarch record view
def search_records(request):
    query = request.GET.get('q', '')
    results = Parishioner.objects.filter(
        models.Q(full_name__icontains=query) |
        models.Q(unique_id__icontains=query) |
        models.Q(parish__icontains=query) |
        models.Q(email__icontains=query)
    )
    return render(request, 'search_results.html', {'results': results, 'query': query})



# Sign up view
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



# Login view
def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            auth_login(request, user)
            
            # Clear any previous error messages
            if 'error' in request.session:
                del request.session['error']
            
            # Check if already verified
            if 'verified_parishioner_id' in request.session:
                return redirect('registry:user_dashboard')
                
            # Set flag to show verification form
            request.session['show_verification'] = True
            request.session.modified = True
            
            return render(request, 'login.html', {
                'user': user,
                'show_verification': True
            })
        else:
            # Store error in session for persistence across redirects
            request.session['error'] = 'Invalid username or password'
            request.session.modified = True
            return redirect('registry:login')
    
    # Clear any existing error messages
    error = None
    if 'error' in request.session:
        error = request.session.pop('error')
        request.session.modified = True
    
    return render(request, 'login.html', {
        'error': error,
        'show_verification': request.session.get('show_verification', False)
    })


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
        
        try:
            parishioner = Parishioner.objects.get(
                unique_id__iexact=unique_id,
                email__iexact=user_email
            )
            
            # Store verification in session
            request.session['verified_parishioner_id'] = parishioner.id
            request.session['verified_parishioner_name'] = parishioner.full_name
            request.session.modified = True
            
            # Clear any verification errors
            if 'verification_error' in request.session:
                del request.session['verification_error']
            
            return redirect('registry:user_dashboard')
            
        except Parishioner.DoesNotExist:
            error_msg = 'No matching parishioner record found'
            if Parishioner.objects.filter(unique_id__iexact=unique_id).exists():
                error_msg = 'Email does not match our records for this ID'
            
            request.session['verification_error'] = error_msg
            request.session['show_verification'] = True
            request.session.modified = True
            return redirect('registry:login')
            
        except Exception as e:
            request.session['verification_error'] = 'An error occurred during verification'
            request.session['show_verification'] = True
            request.session.modified = True
            return redirect('registry:login')
    
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
    
    
# views.py
def submit_birth_record(request):
    if request.method == 'POST':
        try:
            # Parse date strings into date objects
            date_of_birth = parse_date(request.POST.get('date_of_birth'))
            time_of_birth = request.POST.get('time_of_birth')
            baptism_date = parse_date(request.POST.get('baptism_date')) if request.POST.get('baptism_date') else None
            
            # Create BirthRecord record with proper date objects
            birth_record = BirthRecord.objects.create(
                child_name=request.POST.get('child_name'),
                gender=request.POST.get('gender'),
                date_of_birth=date_of_birth,
                time_of_birth=time_of_birth,
                place_of_birth=request.POST.get('place_of_birth'),
                hospital_name=request.POST.get('hospital_name'),
                birth_parish=request.POST.get('parish'),
                baptism_date=baptism_date,
                baptism_certificate=request.POST.get('baptism_certificate'),
                father_unique_id=request.POST.get('father_unique_id'),  # Add this
                father_name=request.POST.get('father_name'),
                father_religion=request.POST.get('father_religion'),
                father_phone=request.POST.get('father_phone'),
                father_parish=request.POST.get('father_parish'),
                mother_unique_id=request.POST.get('mother_unique_id'),  # Add this
                mother_name=request.POST.get('mother_name'),
                mother_maiden=request.POST.get('mother_maiden'),
                mother_religion=request.POST.get('mother_religion'),
                mother_phone=request.POST.get('mother_phone'),
                mother_parish=request.POST.get('mother_parish'),
                home_address=request.POST.get('home_address'),
                father_state=request.POST.get('father_state'),
                father_lga=request.POST.get('father_lga'),
                father_town=request.POST.get('father_town'),
                mother_state=request.POST.get('mother_state'),
                mother_lga=request.POST.get('mother_lga'),
                mother_town=request.POST.get('mother_town'),
            )
            
            # Prepare data for email
            birth_data = {
                'child_name': birth_record.child_name,
                'gender': birth_record.gender,
                'date_of_birth': birth_record.date_of_birth.strftime('%Y-%m-%d') if birth_record.date_of_birth else '',
                'time_of_birth': birth_record.time_of_birth,
                'place_of_birth': birth_record.place_of_birth,
                'hospital_name': birth_record.hospital_name,
                'birth_parish': birth_record.birth_parish,
                'baptism_date': birth_record.baptism_date.strftime('%Y-%m-%d') if birth_record.baptism_date else '',
                'baptism_certificate': birth_record.baptism_certificate,
                'father_unique_id': birth_record.father_unique_id,  # Add this
                'father_name': birth_record.father_name,
                'father_religion': birth_record.father_religion,
                'father_phone': birth_record.father_phone,
                'father_parish': birth_record.father_parish,
                'mother_unique_id': birth_record.mother_unique_id,  # Add this
                'mother_name': birth_record.mother_name,
                'mother_maiden': birth_record.mother_maiden,
                'mother_religion': birth_record.mother_religion,
                'mother_phone': birth_record.mother_phone,
                'mother_parish': birth_record.mother_parish,
                'home_address': birth_record.home_address,
            }
            
            # Send email
            subject = 'New Birth Record Registration'
            html_message = render_to_string('email/birth_registration.html', birth_data)
            plain_message = render_to_string('email/birth_registration.txt', birth_data)
            
            try:
                send_mail(
                    subject,
                    plain_message,
                    settings.DEFAULT_FROM_EMAIL,
                    # [settings.ADMIN_EMAIL],
                    html_message=html_message,
                    fail_silently=False,
                )
                email_sent = True
            except Exception as email_error:
                print(f"Email sending failed: {str(email_error)}")
                email_sent = False
            
            return JsonResponse({
                'success': True,
                'message': 'Birth record registration submitted successfully!',
                'email_sent': email_sent,
                'child_name': birth_record.child_name,
                'baptism_date': birth_record.baptism_date.strftime('%Y-%m-%d') if birth_record.baptism_date else ''
            })
            
        except Exception as e:
            print(f"Error submitting birth record: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    }, status=405)
    
    


@user_passes_test(admin_check, login_url='registry:login')
def birth_records(request):
    # Get filter parameters
    search_query = request.GET.get('q', '')
    parish_filter = request.GET.get('parish', '')
    
    # Initialize base queryset
    if request.user.is_superuser:
        birth_records = BirthRecord.objects.all()
        parishes = Parish.objects.all()  # For superuser dropdown
    else:
        # Get the user's parish
        if hasattr(request.user, 'priestprofile'):
            parish = request.user.priestprofile.parish
        elif hasattr(request.user, 'parishadminprofile'):
            parish = request.user.parishadminprofile.parish
        else:
            parish = None
            
        if parish:
            birth_records = BirthRecord.objects.filter(birth_parish=parish.name)
            parishes = Parish.objects.filter(id=parish.id)  # Only their parish for dropdown
        else:
            birth_records = BirthRecord.objects.none()
            parishes = Parish.objects.none()
    
    # Apply search filter
    if search_query:
        birth_records = birth_records.filter(
            Q(child_name__icontains=search_query) |
            Q(father_name__icontains=search_query) |
            Q(mother_name__icontains=search_query) |
            Q(baptism_certificate__icontains=search_query)
        )
    
    # Apply parish filter (only for superusers)
    if parish_filter and request.user.is_superuser:
        try:
            parish = Parish.objects.get(id=parish_filter)
            birth_records = birth_records.filter(birth_parish=parish.name)
        except Parish.DoesNotExist:
            pass
    
    # Order by baptism date (newest first)
    birth_records = birth_records.order_by('-baptism_date')
    
    # Pagination
    paginator = Paginator(birth_records, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Preserve query parameters for pagination
    query_params = request.GET.copy()
    if 'page' in query_params:
        del query_params['page']
    query_params = query_params.urlencode()
    
    return render(request, 'admin/birth_records.html', {
        'birth_records': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'query_params': query_params,
        'parishes': parishes,  # Pass parishes for the dropdown
    })



@user_passes_test(admin_check, login_url='registry:login')
def add_birth_record(request):  # Changed from add_baptism
    if request.method == 'POST':
        form = BirthRecordForm(request.POST)  # Changed from BaptismForm
        if form.is_valid():
            birth_record = form.save(commit=False)
            birth_record.created_by = request.user
            birth_record.save()
            messages.success(request, 'Birth record added successfully!')  # Changed from Baptism
            return redirect('registry:view_birth_record', birth_record_id=birth_record.id)  # Changed from view_baptism
    else:
        form = BirthRecordForm()  # Changed from BaptismForm
    
    return render(request, 'admin/add_birth_record.html', {'form': form})  # Changed from add_baptism.html

@user_passes_test(admin_check, login_url='registry:login')
def view_birth_record(request, birth_record_id):  # Changed from view_baptism
    birth_record = get_object_or_404(BirthRecord, id=birth_record_id)  # Changed from Baptism
    return render(request, 'admin/view_birth_record.html', {'birth_record': birth_record})  # Changed from baptism




@user_passes_test(lambda u: u.is_superuser or hasattr(u, 'priestprofile'), login_url='registry:login')
def edit_birth_record(request, birth_record_id):
    birth_record = get_object_or_404(BirthRecord, id=birth_record_id)
    
    # For non-superusers, ensure they can only edit records from their own parish
    if not request.user.is_superuser and hasattr(request.user, 'priestprofile'):
        priest_parish = request.user.priestprofile.parish.name
        if birth_record.birth_parish != priest_parish:
            return HttpResponseForbidden("You can only edit birth records from your own parish")
    
    if request.method == 'POST':
        form = BirthRecordForm(request.POST, instance=birth_record)
        if form.is_valid():
            form.save()
            messages.success(request, 'Birth record updated successfully!')
            return redirect('registry:view_birth_record', birth_record_id=birth_record.id)
    else:
        form = BirthRecordForm(instance=birth_record)
    
    return render(request, 'admin/edit_birth_record.html', {
        'form': form,
        'birth_record': birth_record
    })

@user_passes_test(lambda u: u.is_superuser, login_url='registry:login')
def delete_birth_record(request, birth_record_id):  # Changed from delete_baptism
    birth_record = get_object_or_404(BirthRecord, id=birth_record_id)  # Changed from Baptism
    
    if request.method == 'POST':
        birth_record.delete()
        messages.success(request, 'Birth record deleted successfully!')  # Changed from Baptism
        return redirect('registry:birth_records')  # Changed from baptism_records
    
    return render(request, 'admin/confirm_delete_birth_record.html', {'birth_record': birth_record})  # Changed from confirm_delete_baptism.html









#-------------------------------------- Will Go Off ----------------------------------------------------------------------#

from django.http import JsonResponse
from .models import Parishioner

def parishioner_detail(request, unique_id):
    try:
        parishioner = Parishioner.objects.get(unique_id=unique_id)
        data = {
            'full_name': parishioner.full_name,
            'phone_number': parishioner.phone_number,
            'parish': parishioner.parish,
        }
        return JsonResponse(data)
    except Parishioner.DoesNotExist:
        return JsonResponse({'error': 'Parishioner not found'}, status=404)

    
    

def send_otp(phone_number, code):
    # In production, implement actual SMS sending here
    print(f"OTP for {phone_number}: {code}")
    return True




# @user_passes_test(lambda u: u.is_superuser)
# def initial_parish_setup(request):
#     # Check if any parishes exist already
#     if Parish.objects.exists():
#         messages.warning(request, "Initial setup already completed")
#         return redirect('registry:admin_dashboard')
    
#     if request.method == 'POST':
#         # Create parish
#         deanery, _ = Deanery.objects.get_or_create(name=request.POST.get('deanery'))
#         parish = Parish.objects.create(
#             name=request.POST.get('parish'),
#             deanery=deanery,
#             phone_numbers=request.POST.get('phone_numbers')
#         )
        
#         messages.success(request, "Parish setup completed successfully! Priests can now register.")
#         return redirect('registry:admin_dashboard')
    
#     return render(request, 'admin/initial_parish_setup.html')















