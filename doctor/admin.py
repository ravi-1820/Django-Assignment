from django.contrib import admin
from .models import Doctor, Patient

class DoctorAdmin(admin.ModelAdmin):
    list_display = ('name', 'specialty', 'location', 'availability')
    list_filter = ('availability', 'specialty')
    search_fields = ('name', 'location')

admin.site.register(Doctor, DoctorAdmin)
admin.site.register(Patient)
