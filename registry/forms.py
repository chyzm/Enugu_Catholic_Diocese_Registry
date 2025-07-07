# registry/forms.py
from django import forms
from .models import Baptism, Parishioner
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
            'death_verified', 'death_verification_date', 'death_verification_notes'
        ]
        

    
    
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'date_of_death': forms.DateInput(attrs={'type': 'date'}),
            'gender': forms.Select(choices=Parishioner.GENDER_CHOICES),
            'marital_status': forms.Select(choices=Parishioner.MARITAL_STATUS),
            'education_level': forms.RadioSelect(choices=Parishioner.EDUCATION_CHOICES),
            'employment_status': forms.RadioSelect(choices=Parishioner.EMPLOYMENT_CHOICES),
            'deanery': forms.Select(choices=Parishioner.DEANERY_CHOICES),
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
    
    
class BaptismForm(forms.ModelForm):
    class Meta:
        model = Baptism
        fields = '__all__'
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'baptism_date': forms.DateInput(attrs={'type': 'date'}),
            'time_of_birth': forms.TimeInput(attrs={'type': 'time'}),
            'home_address': forms.Textarea(attrs={'rows': 3}),
        }
        
        


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