from django.contrib import admin
from .models import Deanery, Parish

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

# @admin.register(Priest)
# class PriestAdmin(admin.ModelAdmin):
#     list_display = ('full_name', 'parish', 'phone_number', 'email', 'is_active')
#     list_filter = ('parish', 'is_active')
#     search_fields = ('first_name', 'last_name', 'phone_number')

# @admin.register(ParishAdministrator)
# class ParishAdministratorAdmin(admin.ModelAdmin):
#     list_display = ('user', 'parish', 'phone_verified')
#     list_filter = ('parish', 'phone_verified')