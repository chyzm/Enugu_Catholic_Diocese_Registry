from django.contrib import admin
from .models import Deanery, Parish, ParishAdministrator, Priest

@admin.register(Deanery)
class DeaneryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parish_count')
    
    def parish_count(self, obj):
        return obj.parish_set.count()

@admin.register(Parish)
class ParishAdmin(admin.ModelAdmin):
    list_display = ('name', 'deanery', 'phone_numbers')
    list_filter = ('deanery',)
    search_fields = ('name', 'deanery__name')

@admin.register(Priest)
class PriestAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'parish', 'phone_number', 'email', 'is_active')
    list_filter = ('parish', 'is_active')
    search_fields = ('first_name', 'last_name', 'phone_number')

@admin.register(ParishAdministrator)
class ParishAdministratorAdmin(admin.ModelAdmin):
    list_display = ('user', 'parish', 'phone_verified')
    list_filter = ('parish', 'phone_verified')




from .models import Parishioner

@admin.register(Parishioner)
class ParishionerAdmin(admin.ModelAdmin):
    list_display = (
        'full_name', 'unique_id', 'email', 'phone_number', 'gender', 'marital_status',
        'parish', 'deanery', 'station', 'education_level', 'employment_status',
        'state_of_origin', 'lga_of_origin', 'hometown', 'latitude', 'longitude', 'created_at'
    )
    list_filter = (
        'gender', 'marital_status', 'deanery', 'education_level', 
        'employment_status', 'state_of_origin'
    )
    search_fields = ('full_name', 'email', 'phone_number', 'unique_id', 'hometown')
    readonly_fields = ('unique_id', 'created_at', 'updated_at')
    
    fieldsets = (
        ("Personal Information", {
            'fields': (
                'title', 'full_name', 'email', 'phone_number', 'gender', 'date_of_birth',
                'marital_status', 'state_of_origin', 'lga_of_origin', 'hometown'
            )
        }),
        ("Church Details", {
            'fields': (
                'parish', 'deanery', 'station', 'baptized', 'baptism_date',
                'confirmed', 'confirmation_date', 'first_communion', 'first_communion_date'
            )
        }),
        ("Education and Employment", {
            'fields': ('education_level', 'occupation', 'employment_status')
        }),
        ("Marriage Information", {
            'fields': (
                'marriage_verified', 'marriage_verification_date', 'marriage_verification_notes',
                'marriage_date', 'marriage_details'
            )
        }),
        ("Death Information", {
            'fields': (
                'deceased', 'date_of_death', 'death_verified', 
                'death_verification_date', 'death_verification_notes', 'death_details'
            )
        }),
        ("Geolocation", {
            'fields': ('latitude', 'longitude')
        }),
        ("System Fields", {
            'fields': ('unique_id', 'created_by', 'created_at', 'updated_at')
        }),
    )
