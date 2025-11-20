from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, SiteSettings, Notification, ActivityLog, FAQ

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profils'

class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ['site_name', 'maintenance_mode', 'starting_points']
    fieldsets = (
        ('Informations du site', {
            'fields': ('site_name', 'site_description', 'maintenance_mode')
        }),
        ('Paramètres de jeu', {
            'fields': ('starting_points', 'min_bet_amount', 'max_bet_amount')
        }),
        ('Multiplicateurs de gains', {
            'fields': ('exact_multiplier', 'close_multiplier', 'approximate_multiplier')
        }),
    )

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['user__username', 'title', 'message']
    readonly_fields = ['created_at']

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['activity_type', 'user', 'created_at']
    list_filter = ['activity_type', 'created_at']
    search_fields = ['user__username', 'description']
    readonly_fields = ['created_at']

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'order', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['question', 'answer']

# Réenregistrer UserAdmin avec l'inline personnalisé
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)