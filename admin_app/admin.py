from django.contrib import admin
from .models import User_Profile, AuditLog, SystemSettings


@admin.register(User_Profile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone', 'city', 'created_at')
    list_filter = ('role', 'created_at', 'country')
    search_fields = ('user__username', 'user__email', 'phone', 'city')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('User Information', {'fields': ('user',)}),
        ('Profile Details', {'fields': ('role', 'phone', 'address', 'city', 'country', 'profile_picture')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'model_name', 'timestamp', 'ip_address')
    list_filter = ('action', 'model_name', 'timestamp', 'user')
    search_fields = ('user__username', 'description', 'model_name', 'ip_address')
    readonly_fields = ('timestamp', 'user', 'action', 'model_name', 'object_id', 'description', 'ip_address', 'user_agent')
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    list_display = ('key', 'value', 'updated_at')
    search_fields = ('key', 'description')
    readonly_fields = ('updated_at',)
