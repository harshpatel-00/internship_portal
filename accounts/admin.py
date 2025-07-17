from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User
from .models import RecruiterVerification

class CustomUserAdmin(BaseUserAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj and obj.role == 'admin':
            for field in ['user_permissions', 'groups', 'is_superuser', 'is_staff']:
                if field in form.base_fields:
                    form.base_fields.pop(field)
                    
        return form
    
def get_queryset(self, request):
    qs = super().get_queryset(request)
    if request.user.is_superuser:
        return qs
    return qs.exclude(role='students')
admin.site.register(User, CustomUserAdmin)

@admin.register(RecruiterVerification)
class RecruiterVerificationAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'institution', 'is_approved')
    list_filter = ('is_approved',)
    search_fields = ('full_name', 'email', 'institution')