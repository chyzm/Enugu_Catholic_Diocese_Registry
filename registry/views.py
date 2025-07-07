import datetime
from time import timezone
from django.shortcuts import render, redirect, get_object_or_404
from .models import Baptism, Deanery, Parish, Parishioner, Priest, ParishAdministrator
from .forms import BaptismForm, CustomUserCreationForm, ParishAdminCompleteRegistrationForm, ParishAdminSelfRegistrationForm, ParishionerForm, PriestRegistrationForm
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
    
    
def submit_baptism(request):
    if request.method == 'POST':
        try:
            # Parse date strings into date objects
            date_of_birth = parse_date(request.POST.get('date_of_birth'))
            baptism_date = parse_date(request.POST.get('baptism_date')) if request.POST.get('baptism_date') else None
            
            # Create Baptism record with proper date objects
            baptism = Baptism.objects.create(
                child_name=request.POST.get('child_name'),
                gender=request.POST.get('gender'),
                date_of_birth=date_of_birth,
                time_of_birth=request.POST.get('time_of_birth'),
                place_of_birth=request.POST.get('place_of_birth'),
                hospital_name=request.POST.get('hospital_name'),
                birth_parish=request.POST.get('parish'),  # Using parish from form
                baptism_date=baptism_date,
                baptism_certificate=request.POST.get('baptism_certificate'),
                father_name=request.POST.get('father_name'),
                father_religion=request.POST.get('father_religion'),
                father_phone=request.POST.get('father_phone'),
                father_parish=request.POST.get('father_parish'),
                mother_name=request.POST.get('mother_name'),
                mother_maiden=request.POST.get('mother_maiden'),
                mother_religion=request.POST.get('mother_religion'),
                mother_phone=request.POST.get('mother_phone'),
                mother_parish=request.POST.get('mother_parish'),
                home_address=request.POST.get('home_address'),
            )
            
            # Prepare data for email
            baptism_data = {
                'child_name': baptism.child_name,
                'gender': baptism.get_gender_display(),
                'date_of_birth': baptism.date_of_birth.strftime('%Y-%m-%d') if baptism.date_of_birth else '',
                'time_of_birth': str(baptism.time_of_birth) if baptism.time_of_birth else '',
                'place_of_birth': baptism.place_of_birth,
                'hospital_name': baptism.hospital_name,
                'birth_parish': baptism.birth_parish,
                'baptism_date': baptism.baptism_date.strftime('%Y-%m-%d') if baptism.baptism_date else '',
                'baptism_certificate': baptism.baptism_certificate,
                'father_name': baptism.father_name,
                'father_religion': baptism.father_religion,
                'father_phone': baptism.father_phone,
                'father_parish': baptism.father_parish,
                'mother_name': baptism.mother_name,
                'mother_maiden': baptism.mother_maiden,
                'mother_religion': baptism.mother_religion,
                'mother_phone': baptism.mother_phone,
                'mother_parish': baptism.mother_parish,
                'home_address': baptism.home_address,
            }
            
            # Send email to EDC
            subject = 'New Baptism Registration'
            message = render_to_string('email/baptism_registration.txt', baptism_data)
            html_message = render_to_string('email/baptism_registration.html', baptism_data)
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.ADMIN_EMAIL],
                html_message=html_message,
                fail_silently=False,
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Baptism registration submitted successfully!',
                'child_name': baptism.child_name,
                'baptism_date': baptism.baptism_date.strftime('%Y-%m-%d') if baptism.baptism_date else ''
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    })


@user_passes_test(admin_check, login_url='registry:login')
def baptism_records(request):
    # Get filter parameters
    search_query = request.GET.get('q', '')
    parish_filter = request.GET.get('parish', '')
    
    # Build query
    baptisms = Baptism.objects.all().order_by('-baptism_date')
    
    if search_query:
        baptisms = baptisms.filter(
            Q(child_name__icontains=search_query) |
            Q(father_name__icontains=search_query) |
            Q(mother_name__icontains=search_query) |
            Q(baptism_certificate__icontains=search_query)
        )
    
    if parish_filter:
        baptisms = baptisms.filter(birth_parish=parish_filter)
    
    # Pagination
    paginator = Paginator(baptisms, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Preserve query parameters for pagination
    query_params = request.GET.copy()
    if 'page' in query_params:
        del query_params['page']
    query_params = query_params.urlencode()
    
    return render(request, 'admin/baptism_records.html', {
        'baptisms': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'query_params': query_params,
        'deanery_choices': Parishioner.DEANERY_CHOICES,
    })
    
    
@user_passes_test(admin_check, login_url='registry:login')
def add_baptism(request):
    if request.method == 'POST':
        form = BaptismForm(request.POST)
        if form.is_valid():
            baptism = form.save(commit=False)
            baptism.created_by = request.user
            baptism.save()
            messages.success(request, 'Baptism record added successfully!')
            return redirect('registry:view_baptism', baptism_id=baptism.id)
    else:
        form = BaptismForm()
    
    return render(request, 'admin/add_baptism.html', {'form': form})

@user_passes_test(admin_check, login_url='registry:login')
def view_baptism(request, baptism_id):
    baptism = get_object_or_404(Baptism, id=baptism_id)
    return render(request, 'admin/view_baptism.html', {'baptism': baptism})

@user_passes_test(admin_check, login_url='registry:login')
def edit_baptism(request, baptism_id):
    baptism = get_object_or_404(Baptism, id=baptism_id)
    
    if request.method == 'POST':
        form = BaptismForm(request.POST, instance=baptism)
        if form.is_valid():
            form.save()
            messages.success(request, 'Baptism record updated successfully!')
            return redirect('registry:view_baptism', baptism_id=baptism.id)
    else:
        form = BaptismForm(instance=baptism)
    
    return render(request, 'admin/edit_baptism.html', {
        'form': form,
        'baptism': baptism
    })

@user_passes_test(lambda u: u.is_superuser, login_url='registry:login')
def delete_baptism(request, baptism_id):
    baptism = get_object_or_404(Baptism, id=baptism_id)
    
    if request.method == 'POST':
        baptism.delete()
        messages.success(request, 'Baptism record deleted successfully!')
        return redirect('registry:baptism_records')
    
    return render(request, 'admin/confirm_delete_baptism.html', {'baptism': baptism})


@user_passes_test(admin_check, login_url='registry:login')
def add_baptism(request):
    if request.method == 'POST':
        form = BaptismForm(request.POST)
        if form.is_valid():
            baptism = form.save(commit=False)
            baptism.created_by = request.user
            
            # Try to link to parishioner if child name matches
            try:
                parishioner = Parishioner.objects.filter(
                    Q(full_name__icontains=baptism.child_name.split()[0]) |
                    Q(family_details__icontains=baptism.child_name)
                ).first()
                if parishioner:
                    baptism.parishioner = parishioner
                    parishioner.baptized = True
                    parishioner.baptism_date = baptism.baptism_date
                    parishioner.save()
            except Exception as e:
                print(f"Error linking baptism to parishioner: {e}")
            
            baptism.save()
            messages.success(request, 'Baptism record added successfully!')
            return redirect('registry:view_baptism', baptism_id=baptism.id)
    else:
        form = BaptismForm()
    
    return render(request, 'admin/add_baptism.html', {'form': form})



def parish_admin_register(request):
    if request.method == 'POST' and 'verify_phone' in request.POST:
        form = ParishAdminSelfRegistrationForm(request.POST)
        if form.is_valid():
            priest = form.cleaned_data['priest']
            
            # Generate verification code (6 digits)
            verification_code = ''.join(random.choices('0123456789', k=6))
            expiry = timezone.now() + datetime.timedelta(minutes=30)
            
            # Store in session
            request.session['parish_admin_registration'] = {
                'priest_id': priest.id,
                'verification_code': verification_code,
                'expiry': expiry.isoformat(),
                'attempts': 0  # Track verification attempts
            }
            
            # In production, send via SMS service
            print(f"OTP for {priest.phone_number}: {verification_code}")  # Remove in production
            
            messages.info(request, f"A verification code has been sent to {priest.phone_number}")
            return redirect('registry:parish_admin_verify')
    else:
        form = ParishAdminSelfRegistrationForm()
    
    return render(request, 'parish_admin/register.html', {'form': form})




def parish_admin_verify(request):
    session_data = request.session.get('parish_admin_registration')
    if not session_data:
        messages.error(request, "Registration session expired")
        return redirect('registry:parish_admin_register')
    
    try:
        priest = Priest.objects.get(id=session_data['priest_id'])
        expiry = datetime.fromisoformat(session_data['expiry'])
        
        if request.method == 'POST':
            entered_code = request.POST.get('verification_code', '').strip()
            
            # Check attempts
            if session_data['attempts'] >= 3:
                del request.session['parish_admin_registration']
                messages.error(request, "Too many failed attempts. Please start again.")
                return redirect('registry:parish_admin_register')
            
            # Check if code matches
            if entered_code == session_data['verification_code']:
                if timezone.now() < expiry:
                    request.session['parish_admin_verified'] = True
                    return redirect('registry:parish_admin_complete')
                else:
                    messages.error(request, "Verification code has expired")
            else:
                # Increment attempts
                session_data['attempts'] += 1
                request.session['parish_admin_registration'] = session_data
                messages.error(request, "Invalid verification code")
        
        return render(request, 'parish_admin/verify.html', {
            'phone': priest.phone_number[-4:],  # Show last 4 digits for privacy
            'expiry_minutes': (expiry - timezone.now()).seconds // 60
        })
        
    except Priest.DoesNotExist:
        messages.error(request, "Invalid registration session")
        return redirect('registry:parish_admin_register')

def parish_admin_complete(request):
    if not request.session.get('parish_admin_verified'):
        messages.error(request, "Verification required")
        return redirect('registry:parish_admin_register')
    
    session_data = request.session.get('parish_admin_registration')
    if not session_data:
        messages.error(request, "Registration session expired")
        return redirect('registry:parish_admin_register')
    
    priest = get_object_or_404(Priest, id=session_data['priest_id'])
    
    if request.method == 'POST':
        form = ParishAdminCompleteRegistrationForm(request.POST, priest=priest)
        if form.is_valid():
            # Create user
            user = form.save(commit=False)
            user.email = priest.email
            user.is_staff = True
            user.save()
            
            # Create ParishAdmin profile
            ParishAdministrator.objects.create(
                user=user,
                parish=priest.parish,
                priest=priest,
                phone_verified=True
            )
            
            # Clean up session
            del request.session['parish_admin_registration']
            del request.session['parish_admin_verified']
            
            # Log in the user
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('registry:parish_admin_dashboard')
    else:
        form = ParishAdminCompleteRegistrationForm(priest=priest)
    
    return render(request, 'parish_admin/complete.html', {
        'form': form,
        'priest': priest
    })

@login_required
def parish_admin_dashboard(request):
    try:
        # Check if user is a parish admin
        parish_admin = request.user.parishadministrator
        parish = parish_admin.parish
        
        # Only show parishioners from this parish
        parishioners = Parishioner.objects.filter(parish=parish.name).order_by('-created_at')
        
        # Get counts for dashboard
        stats = {
            'total_parishioners': parishioners.count(),
            'baptized_count': parishioners.filter(baptized=True).count(),
            'confirmed_count': parishioners.filter(confirmed=True).count(),
            'deceased_count': parishioners.filter(deceased=True).count(),
        }
        
        return render(request, 'parish_admin/dashboard.html', {
            'parish': parish,
            'stats': stats,
            'parishioners': parishioners[:10]  # Show recent 10
        })
        
    except (ParishAdministrator.DoesNotExist, AttributeError):
        messages.error(request, "Access restricted to parish administrators")
        return redirect('registry:home')



# @login_required
# def parish_admin_dashboard(request):
#     try:
#         # Check if user is a parish admin
#         parish_admin = request.user.parishadministrator
#         parish = parish_admin.parish
        
#         # Only show parishioners from this parish
#         parishioners = Parishioner.objects.filter(parish=parish.name).order_by('-created_at')
        
#         # Get counts for dashboard
#         stats = {
#             'total_parishioners': parishioners.count(),
#             'baptized_count': parishioners.filter(baptized=True).count(),
#             'confirmed_count': parishioners.filter(confirmed=True).count(),
#             'deceased_count': parishioners.filter(deceased=True).count(),
#         }
        
#         return render(request, 'parish_admin/dashboard.html', {
#             'parish': parish,
#             'stats': stats,
#             'parishioners': parishioners[:10]  # Show recent 10
#         })
        
#     except (ParishAdministrator.DoesNotExist, AttributeError):
#         messages.error(request, "Access restricted to parish administrators")
#         return redirect('registry:home')
    
    
    
# views.py
from django.http import JsonResponse

def get_parishes_by_deanery(request):
    deanery_id = request.GET.get('deanery_id')
    parishes = Parish.objects.filter(deanery_id=deanery_id).values('id', 'name')
    return JsonResponse(list(parishes), safe=False)
    
    
    

# views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ParishSetupForm, PriestSetupForm

# @user_passes_test(lambda u: u.is_superuser)
# def initial_parish_setup(request):
#     # Check if any parishes exist already
#     if Parish.objects.exists():
#         messages.warning(request, "Initial setup already completed")
#         return redirect('admin:index')
    
#     if request.method == 'POST':
#         parish_form = ParishSetupForm(request.POST)
#         priest_form = PriestSetupForm(request.POST)
        
#         if parish_form.is_valid() and priest_form.is_valid():
#             # Create parish
#             parish = parish_form.save()
            
#             # Create priest (the first admin)
#             priest = priest_form.save(commit=False)
#             priest.parish = parish
#             priest.is_active = True
#             priest.save()
            
#             # Create user account for priest
#             from django.contrib.auth.models import User
#             user = User.objects.create_user(
#                 username=priest.email.split('@')[0],
#                 email=priest.email,
#                 password=priest_form.cleaned_data['password']
#             )
#             user.is_staff = True
#             user.save()
            
#             # Create parish admin record
#             ParishAdministrator.objects.create(
#                 user=user,
#                 parish=parish,
#                 priest=priest,
#                 phone_verified=True
#             )
            
#             messages.success(request, "Initial parish setup completed successfully!")
#             return redirect('admin:index')
#     else:
#         parish_form = ParishSetupForm()
#         priest_form = PriestSetupForm()
    
#     return render(request, 'admin/initial_parish_setup.html', {
#         'parish_form': parish_form,
#         'priest_form': priest_form
#     })



# @user_passes_test(lambda u: u.is_superuser)
# def initial_parish_setup(request):
#     # Check if any parishes exist already
#     if Parish.objects.exists():
#         messages.warning(request, "Initial setup already completed")
#         return redirect('registry:admin_dashboard')
    
#     if request.method == 'POST':
#         # Create parish
#         parish = Parish.objects.create(
#             name=request.POST.get('parish'),
#             deanery=Deanery.objects.get_or_create(name=request.POST.get('deanery'))[0],
#             phone_numbers=request.POST.get('phone_numbers'),
#             # email=request.POST.get('email')
#         )
        
#         # Create priest (the first admin)
#         priest = Priest.objects.create(
#             # first_name=request.POST.get('first_name'),
#             # last_name=request.POST.get('last_name'),
#             # email=request.POST.get('priest_email'),
#             phone_number=request.POST.get('priest_phone'),
#             parish=parish,
#             is_active=True
#         )
        
#         # Create user account for priest
#         from django.contrib.auth.models import User
#         user = User.objects.create_user(
#             username=request.POST.get('priest_email').split('@')[0],
#             email=request.POST.get('priest_email'),
#             password=request.POST.get('password')
#         )
#         user.is_staff = True
#         user.save()
        
#         # Create parish admin record
#         ParishAdministrator.objects.create(
#             user=user,
#             parish=parish,
#             priest=priest,
#             phone_verified=True
#         )
        
#         messages.success(request, "Initial parish setup completed successfully!")
#         return redirect('registry:admin_dashboard')
    
#     return render(request, 'admin/initial_parish_setup.html')



@user_passes_test(lambda u: u.is_superuser)
def initial_parish_setup(request):
    # Check if any parishes exist already
    if Parish.objects.exists():
        messages.warning(request, "Initial setup already completed")
        return redirect('registry:admin_dashboard')
    
    if request.method == 'POST':
        # Create parish
        deanery, _ = Deanery.objects.get_or_create(name=request.POST.get('deanery'))
        parish = Parish.objects.create(
            name=request.POST.get('parish'),
            deanery=deanery,
            phone_numbers=request.POST.get('phone_numbers')
        )
        
        messages.success(request, "Parish setup completed successfully! Priests can now register.")
        return redirect('registry:admin_dashboard')
    
    return render(request, 'admin/initial_parish_setup.html')




from django.contrib.auth import get_user_model
User = get_user_model()

def priest_register(request):
    if request.method == 'POST':
        form = PriestRegistrationForm(request.POST)
        if form.is_valid():
            try:
                # Create priest first
                priest = form.save(commit=False)
                priest.is_active = True
                priest.save()
                
                # Create user account
                user = User.objects.create_user(
                    username=form.cleaned_data['email'].split('@')[0],
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password1'],
                    is_staff=True
                )
                
                # Create parish admin record
                ParishAdministrator.objects.create(
                    user=user,
                    parish=priest.parish,
                    priest=priest,
                    phone_verified=True
                )
                
                # Generate and send verification code
                verification_code = generate_verification_code()
                send_otp(priest.phone_number, verification_code)
                
                # Store in session for verification
                request.session['priest_verification'] = {
                    'user_id': user.id,
                    'verification_code': verification_code,
                    'expiry': (timezone.now() + datetime.timedelta(minutes=30)).isoformat()
                }
                
                messages.info(request, "A verification code has been sent to your phone")
                return redirect('registry:priest_verify')
                
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
                return redirect('registry:priest_register')
    else:
        form = PriestRegistrationForm()
    
    return render(request, 'register.html', {
        'form': form,
        'parishes': Parish.objects.all()
    })

def priest_verify(request):
    session_data = request.session.get('priest_verification')
    if not session_data:
        messages.error(request, "Verification session expired")
        return redirect('registry:priest_register')
    
    if request.method == 'POST':
        entered_code = request.POST.get('verification_code')
        
        if entered_code == session_data['verification_code']:
            # Verification successful - log in the user
            user = User.objects.get(id=session_data['user_id'])
            login(request, user)
            
            # Clear session
            del request.session['priest_verification']
            
            messages.success(request, "Verification successful! You are now logged in.")
            return redirect('registry:parish_admin_dashboard')
        else:
            messages.error(request, "Invalid verification code")
    
    return render(request, 'verify.html')



def priest_verify(request):
    session_data = request.session.get('priest_verification')
    if not session_data:
        messages.error(request, "Verification session expired")
        return redirect('registry:priest_register')
    
    if request.method == 'POST':
        entered_code = request.POST.get('verification_code')
        
        if entered_code == session_data['verification_code']:
            # Verification successful
            priest = Priest.objects.get(id=session_data['priest_id'])
            user = priest.parishadministrator.user
            
            # Log in the user
            login(request, user)
            
            # Clear session
            del request.session['priest_verification']
            
            messages.success(request, "Verification successful! You are now logged in.")
            return redirect('registry:parish_admin_dashboard')
        else:
            messages.error(request, "Invalid verification code")
    
    return render(request, 'verify.html')

def send_otp(phone_number, code):
    # In production, implement actual SMS sending here
    print(f"OTP for {phone_number}: {code}")
    return True