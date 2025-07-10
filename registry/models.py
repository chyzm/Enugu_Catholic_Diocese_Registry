from datetime import timezone
from django.db import models
from django.db import models
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.contrib.auth.models import Group


# Create your models here.

GENDER_CHOICES = [('M', 'Male'), ('F', 'Female')] # this was done so baptism can use name attribute.
class Parishioner(models.Model):
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female')]
    MARITAL_STATUS = [
        ('S', 'Single'),
        ('M', 'Married'),
        ('D', 'Divorced'),
        ('W', 'Widowed'),
        ('E', 'Separated')  # Added Separated with code 'E'
    ]
    
    EDUCATION_CHOICES = [
        ('PRIMARY', 'Primary'),
        ('SECONDARY', 'Secondary'),
        ('UNDERGRAD', 'Undergraduate'),
        ('MASTERS', 'Masters'),
        ('POSTGRAD', 'Post-Graduate')
    ]
    
    EMPLOYMENT_CHOICES = [
        ('EMPLOYED', 'Employed'),
        ('UNEMPLOYED', 'Unemployed'),
        ('SELF_EMPLOYED', 'Self Employed')
    ]
    
    DEANERY_CHOICES = [
        ('Agbani Deanery', 'Agbani Deanery'),
        ('Aguobu Owa Deanery', 'Aguobu Owa Deanery'),
        ('Emene Deanery', 'Emene Deanery'),
        ('Enugu Deanery', 'Enugu Deanery'),
        ('Nkwo Nike Deanery', 'Nkwo Nike Deanery'),
        ('Udi Deanery', 'Udi Deanery'),
        ('Chaplaincy', 'Chaplaincy'),
        
    ]
    
    # Personal Information
    unique_id = models.CharField(max_length=20, unique=True, blank=True)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True, unique=True)
    title = models.CharField(max_length=50, blank=True)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    marital_status = models.CharField(max_length=1, choices=MARITAL_STATUS, blank=True)
    phone_number = models.CharField(max_length=20)
    
    # Church Details
    parish = models.CharField(max_length=100)
    deanery = models.CharField(max_length=100, blank=True, null=True, choices=DEANERY_CHOICES)
    station = models.CharField(max_length=100)
    baptized = models.BooleanField(default=False)
    baptism_date = models.DateField(null=True, blank=True)
    confirmed = models.BooleanField(default=False)
    confirmation_date = models.DateField(null=True, blank=True)
    first_communion = models.BooleanField(default=False)
    first_communion_date = models.DateField(null=True, blank=True)
    
    # Education and Occupation
    education_level = models.CharField(max_length=20, choices=EDUCATION_CHOICES, blank=True)
    occupation = models.CharField(max_length=100, blank=True)
    employment_status = models.CharField(max_length=20, choices=EMPLOYMENT_CHOICES, blank=True)
    
    # Family Details
    family_details = models.TextField(blank=True)
    
    
    # Location
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    
  

    
    # Marital verification
    marriage_verified = models.BooleanField(default=False)
    marriage_verification_date = models.DateField(null=True, blank=True)
    marriage_verification_notes = models.TextField(blank=True)
    marriage_date = models.DateField(null=True, blank=True)
    marriage_details = models.TextField(blank=True)
    
    # Death verification
    death_verified = models.BooleanField(default=False)
    death_verification_date = models.DateField(null=True, blank=True)
    death_verification_notes = models.TextField(null=True, blank=True)
    deceased = models.BooleanField(default=False)
    date_of_death = models.DateField(null=True, blank=True)
    death_details = models.TextField(blank=True)
    
    
    # System
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    def save(self, *args, **kwargs):
        if not self.unique_id:
            # Generate unique ID: first 3 letters of surname + dash + 6 digits
            surname = self.full_name.split()[-1][:3].upper()
            random_digits = get_random_string(6, allowed_chars='0123456789')
            self.unique_id = f"{surname}-{random_digits}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.full_name} ({self.unique_id})"
    
    

# models.py
class BirthRecord(models.Model):  # Changed from Baptism
    parishioner = models.ForeignKey(Parishioner, on_delete=models.SET_NULL, null=True, blank=True, related_name='birth_records')  # Changed from baptisms
    child_name = models.CharField(max_length=255)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    date_of_birth = models.DateField()
    time_of_birth = models.TimeField()
    place_of_birth = models.CharField(max_length=255)
    hospital_name = models.CharField(max_length=255, blank=True, null=True)
    birth_parish = models.CharField(max_length=100)
    baptism_date = models.DateField(blank=True, null=True)
    baptism_certificate = models.CharField(max_length=50, blank=True, null=True)
    father_name = models.CharField(max_length=255)
    father_religion = models.CharField(max_length=50)
    father_phone = models.CharField(max_length=20)
    father_parish = models.CharField(max_length=100, blank=True, null=True)
    mother_name = models.CharField(max_length=255)
    mother_maiden = models.CharField(max_length=255, blank=True, null=True)
    mother_religion = models.CharField(max_length=50)
    mother_phone = models.CharField(max_length=20)
    mother_parish = models.CharField(max_length=100, blank=True, null=True)
    father_unique_id = models.CharField(max_length=50, blank=True, null=True)
    mother_unique_id = models.CharField(max_length=50, blank=True, null=True)
    father_state = models.CharField(max_length=100, blank=True, null=True)
    father_lga = models.CharField(max_length=100, blank=True, null=True)
    father_town = models.CharField(max_length=100, blank=True, null=True)
    mother_state = models.CharField(max_length=100, blank=True, null=True)
    mother_lga = models.CharField(max_length=100, blank=True, null=True)
    mother_town = models.CharField(max_length=100, blank=True, null=True)
    home_address = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.child_name} - {self.date_of_birth}"
    
    
    


class Deanery(models.Model):
    name = models.CharField(max_length=255, unique=True)
    
    def __str__(self):
        return self.name

class Parish(models.Model):
    name = models.CharField(max_length=255, unique=True)
    deanery = models.ForeignKey(Deanery, on_delete=models.PROTECT)
   # This field will store comma-separated approved phone numbers for the parish
    phone_numbers = models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        return f"{self.name} ({self.deanery})"
    
    def get_approved_numbers_list(self):
        """Returns list of approved phone numbers"""
        return [num.strip() for num in self.phone_numbers.split(',') if num.strip()]
    
    def is_approved_number(self, phone_number):
        """Check if a phone number is approved for this parish"""
        return phone_number in self.get_approved_numbers_list()
    
    
    
    
# models.py
from django.contrib.auth.models import User, Group

class PriestProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    parish = models.ForeignKey(Parish, on_delete=models.PROTECT)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_priests')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Priest: {self.user.get_full_name()} ({self.parish.name})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        group, _ = Group.objects.get_or_create(name='Priest')
        self.user.groups.add(group)
        self.user.is_staff = True
        self.user.save()

class ParishAdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    parish = models.ForeignKey(Parish, on_delete=models.PROTECT)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_admins')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Admin: {self.user.username} ({self.parish.name})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        group, _ = Group.objects.get_or_create(name='Parish Admin')
        self.user.groups.add(group)
        self.user.is_staff = True
        self.user.save()

    
    
    

# class Priest(models.Model):
#     first_name = models.CharField(max_length=100)
#     last_name = models.CharField(max_length=100)
#     email = models.EmailField(unique=True)
#     phone_number = models.CharField(max_length=20)
#     parish = models.ForeignKey(Parish, on_delete=models.PROTECT)
#     is_active = models.BooleanField(default=True)
    
#     @property
#     def full_name(self):
#         return f"{self.first_name} {self.last_name}"
    
#     def __str__(self):
#         return f"{self.full_name} ({self.parish.name})"


# class Priest(models.Model):
#     first_name = models.CharField(max_length=100)
#     last_name = models.CharField(max_length=100)
#     email = models.EmailField(unique=True)
#     phone_number = models.CharField(max_length=20)
#     parish = models.ForeignKey(Parish, on_delete=models.PROTECT)
#     is_active = models.BooleanField(default=True)
#     created_at = models.DateTimeField(default=timezone.now)  # Only use default
    
#     @property
#     def full_name(self):
#         return f"{self.first_name} {self.last_name}"
    
#     def __str__(self):
#         return f"{self.full_name} ({self.parish.name})"
    
    



# class ParishAdministrator(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     parish = models.ForeignKey(Parish, on_delete=models.PROTECT)
#     priest = models.ForeignKey(Priest, on_delete=models.PROTECT)  # Changed from OneToOne
#     phone_verified = models.BooleanField(default=False)
#     verification_code = models.CharField(max_length=6, blank=True, null=True)
#     verification_code_expiry = models.DateTimeField(blank=True, null=True)
#     created_at = models.DateTimeField(default=timezone.now)  # Only use default
#     def __str__(self):
#         return f"{self.user.username} - {self.parish.name}"