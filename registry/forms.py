# registry/forms.py
from django import forms
from .models import BirthRecord, Parish, Parishioner
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class ParishionerForm(forms.ModelForm):
    class Meta:
        model = Parishioner
        fields = [
            'title', 'full_name', 'email', 'date_of_birth', 'gender', 'phone_number',
            'marital_status', 'parish', 'deanery', 'station', 'baptized', 'confirmed', 
            'first_communion', 'education_level', 'occupation', 'employment_status',
            'deceased', 'date_of_death', 'death_details',
            'marriage_verified', 'marriage_verification_date', 'marriage_verification_notes',
            'death_verified', 'death_verification_date', 'death_verification_notes',
            'state_of_origin', 'lga_of_origin', 'town', 'marriage_date','marriage_details',

        ]
        

    
    
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'date_of_death': forms.DateInput(attrs={'type': 'date'}),
            'gender': forms.Select(choices=Parishioner.GENDER_CHOICES),
            'marital_status': forms.Select(choices=Parishioner.MARITAL_STATUS),
            'education_level': forms.RadioSelect(choices=Parishioner.EDUCATION_CHOICES),
            'employment_status': forms.RadioSelect(choices=Parishioner.EMPLOYMENT_CHOICES),
            'deanery': forms.Select(choices=Parishioner.DEANERY_CHOICES),
            'education_level': forms.Select(attrs={'class': 'form-select'}),
            'employment_status': forms.Select(attrs={'class': 'form-select'}),
        }



        
        
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:  # Only validate if email is provided
            if Parishioner.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("This email is already registered.")
        return email
    
    
    
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    unique_id = forms.CharField(required=True, max_length=20, label="Unique Parishioner ID")

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        unique_id = cleaned_data.get('unique_id')
        
        # Verify parishioner record exists with matching email and ID
        if email and unique_id:
            if not Parishioner.objects.filter(
                unique_id__iexact=unique_id,
                email__iexact=email
            ).exists():
                raise forms.ValidationError(
                    "No parishioner record found with this ID and email combination"
                )
        return cleaned_data
    
    
# forms.py
class BirthRecordForm(forms.ModelForm):
    father_unique_id = forms.CharField(required=False, label="Father's Unique ID")
    mother_unique_id = forms.CharField(required=False, label="Mother's Unique ID")

# forms.py
class BirthRecordForm(forms.ModelForm):
    father_unique_id = forms.CharField(required=False, label="Father's Unique ID")
    mother_unique_id = forms.CharField(required=False, label="Mother's Unique ID")

    class Meta:
        model = BirthRecord
        model = BirthRecord
        fields = '__all__'
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'baptism_date': forms.DateInput(attrs={'type': 'date'}),
            'time_of_birth': forms.TimeInput(attrs={'type': 'time'}),
            'home_address': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make these fields not required since they'll be populated from parishioner data
        self.fields['father_name'].required = False
        self.fields['mother_name'].required = False
        self.fields['father_phone'].required = False
        self.fields['mother_phone'].required = False

    def clean_father_unique_id(self):
        unique_id = self.cleaned_data.get('father_unique_id')
        if unique_id:
            try:
                parishioner = Parishioner.objects.get(unique_id__iexact=unique_id)
                if parishioner.gender != 'M':
                    raise forms.ValidationError("This ID belongs to a female parishioner")
                return unique_id
            except Parishioner.DoesNotExist:
                raise forms.ValidationError("No parishioner found with this ID")
        return unique_id

    def clean_mother_unique_id(self):
        unique_id = self.cleaned_data.get('mother_unique_id')
        if unique_id:
            try:
                parishioner = Parishioner.objects.get(unique_id__iexact=unique_id)
                if parishioner.gender != 'F':
                    raise forms.ValidationError("This ID belongs to a male parishioner")
                return unique_id
            except Parishioner.DoesNotExist:
                raise forms.ValidationError("No parishioner found with this ID")
        return unique_id

    def clean(self):
        cleaned_data = super().clean()
        
        # Populate father's information if ID is provided
        father_id = cleaned_data.get('father_unique_id')
        if father_id:
            try:
                father = Parishioner.objects.get(unique_id__iexact=father_id)
                cleaned_data['father_name'] = father.full_name
                cleaned_data['father_phone'] = father.phone_number
                cleaned_data['father_parish'] = father.parish
            except Parishioner.DoesNotExist:
                pass
        
        # Populate mother's information if ID is provided
        mother_id = cleaned_data.get('mother_unique_id')
        if mother_id:
            try:
                mother = Parishioner.objects.get(unique_id__iexact=mother_id)
                cleaned_data['mother_name'] = mother.full_name
                cleaned_data['mother_phone'] = mother.phone_number
                cleaned_data['mother_parish'] = mother.parish
            except Parishioner.DoesNotExist:
                pass
        
        return cleaned_data
    
    
class PriestAssignmentForm(forms.Form):
    user = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True).exclude(priestprofile__isnull=False),
        label="Select User (Not already a Priest)",
        help_text="Only active users who aren't already assigned as priests.",
        widget=forms.Select(attrs={"class": "form-control"})
    )
    parish = forms.ModelChoiceField(
        queryset=Parish.objects.all(),
        label="Assign to Parish",
        widget=forms.Select(attrs={"class": "form-control"})
    )


class AdminAssignmentForm(forms.Form):
    user = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True).exclude(parishadminprofile__isnull=False),
        label="Select User (Not already a Parish Admin)",
        help_text="Only active users who aren't already parish admins.",
        widget=forms.Select(attrs={"class": "form-control"})
    )
    parish = forms.ModelChoiceField(
        queryset=Parish.objects.all(),
        label="Assign to Parish",
        widget=forms.Select(attrs={"class": "form-control"})
    )

        
#---------------------------------------------------------------------------------------------------------------------------

# class ParishAdminSelfRegistrationForm(forms.Form):
#     phone_number = forms.CharField(required=True)
#     email = forms.EmailField(required=True)
    
#     def clean(self):
#         cleaned_data = super().clean()
#         phone_number = cleaned_data.get('phone_number')
#         email = cleaned_data.get('email').lower()
        
#         try:
#             # Check if priest exists with this phone and email
#             priest = Priest.objects.get(
#                 phone_number=phone_number,
#                 email__iexact=email,
#                 is_active=True
#             )
            
#             # Verify phone is approved for parish
#             if not priest.parish.is_approved_number(phone_number):
#                 raise forms.ValidationError("This phone number is not approved for your parish")
            
#             cleaned_data['priest'] = priest
#             return cleaned_data
            
#         except Priest.DoesNotExist:
#             raise forms.ValidationError("No active priest found with this phone number and email")
        
        
        
        
# class ParishAdminCompleteRegistrationForm(UserCreationForm):
#     class Meta:
#         model = User
#         fields = ("username", "password1", "password2")
    
#     def __init__(self, *args, **kwargs):
#         from .models import Priest  # Ensure this is imported locally if needed
#         self.priest = kwargs.pop('priest', None)
#         super().__init__(*args, **kwargs)
#         if self.priest:
#             self.fields['username'].initial = self.priest.email.split('@')[0]
            
            
            

# # class ParishSetupForm(forms.ModelForm):
# #     class Meta:
# #         model = Parish
# #         fields = ['name', 'deanery', 'approved_phone_numbers']
# #         widgets = {
# #             'approved_phone_numbers': forms.TextInput(attrs={
# #                 'placeholder': '+2348012345678,+2348098765432'
# #             })
# #         }


# class PriestRegistrationForm(forms.ModelForm):
#     password1 = forms.CharField(widget=forms.PasswordInput)
#     password2 = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")
    
#     class Meta:
#         model = Priest
#         fields = ['first_name', 'last_name', 'email', 'phone_number', 'parish']
    
#     def clean(self):
#         cleaned_data = super().clean()
#         password1 = cleaned_data.get('password1')
#         password2 = cleaned_data.get('password2')
        
#         if password1 and password2 and password1 != password2:
#             raise forms.ValidationError("Passwords don't match")
            
#         # Verify phone number is approved for parish
#         parish = cleaned_data.get('parish')
#         phone_number = cleaned_data.get('phone_number')
#         if parish and phone_number and not parish.is_approved_number(phone_number):
#             raise forms.ValidationError("This phone number is not approved for the selected parish")
        
#         return cleaned_data


        
# class ParishSetupForm(forms.ModelForm):
#     class Meta:
#         model = Parish
#         fields = ['name', 'deanery', 'phone_numbers']  # Changed from approved_phone_numbers
#         widgets = {
#             'phone_numbers': forms.TextInput(attrs={
#                 'placeholder': '+2348012345678,+2348098765432'
#             })
#         }

# class PriestSetupForm(forms.ModelForm):
#     password = forms.CharField(widget=forms.PasswordInput)
#     password_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")
    
#     class Meta:
#         model = Priest
#         fields = ['first_name', 'last_name', 'email', 'phone_number']
    
#     def clean(self):
#         cleaned_data = super().clean()
#         if cleaned_data.get('password') != cleaned_data.get('password_confirm'):
#             raise forms.ValidationError("Passwords don't match")
#         return cleaned_data
        
        


# class CustomUserCreationForm(UserCreationForm):
#     email = forms.EmailField(required=True)
#     unique_id = forms.CharField(required=True, max_length=20, label="Unique Parishioner ID")

#     class Meta:
#         model = User
#         fields = ("username", "email", "password1", "password2")

#     def clean(self):
#         cleaned_data = super().clean()
#         email = cleaned_data.get('email')
#         unique_id = cleaned_data.get('unique_id')
        
#         # Verify parishioner record exists with matching email and ID
#         if email and unique_id:
#             if not Parishioner.objects.filter(
#                 unique_id__iexact=unique_id,
#                 email__iexact=email
#             ).exists():
#                 raise forms.ValidationError(
#                     "No parishioner record found with this ID and email combination"
#                 )
#         return cleaned_data

#     def save(self, commit=True):
#         user = super().save(commit=False)
#         user.email = self.cleaned_data["email"]
#         if commit:
#             user.save()
#         return user