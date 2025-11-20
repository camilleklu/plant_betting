from django.contrib import admin
from .models import Plant, Criterion, PlantMeasurement
from django.utils import timezone
from django.contrib import messages
from django.utils.html import format_html

class PlantMeasurementInline(admin.TabularInline):
    """
    Inline pour afficher les mesures dans l'admin des plantes
    """
    model = PlantMeasurement
    extra = 0
    readonly_fields = ['measured_at']
    fields = ['criterion', 'value', 'unit_display', 'measured_at', 'notes']
    
    def unit_display(self, obj):
        return obj.criterion.unit
    unit_display.short_description = 'Unité'

class PlantAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'species', 'category', 'owner', 'obtaining_date', 
        'death_date', 'is_active', 'days_alive_display', 'image_preview'
    ]
    list_filter = [
        'is_active', 'category', 'species', 'obtaining_date', 'created_at'
    ]
    search_fields = ['name', 'species', 'owner__username']
    readonly_fields = ['created_at', 'days_alive', 'image_preview_large']
    list_per_page = 20
    date_hierarchy = 'obtaining_date'
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('name', 'species', 'category', 'owner')
        }),
        ('Dates', {
            'fields': ('obtaining_date', 'death_date')
        }),
        ('Image', {
            'fields': ('image', 'image_preview_large')
        }),
        ('Statut', {
            'fields': ('is_active', 'created_at', 'days_alive')
        }),
    )
    
    inlines = [PlantMeasurementInline]
    
    actions = ['mark_as_dead', 'mark_as_alive', 'recalculate_days_alive']
    
    def mark_as_dead(self, request, queryset):
        """
        Marquer les plantes sélectionnées comme mortes
        """
        from bets.models import Bet
        
        updated_count = 0
        for plant in queryset.filter(is_active=True):
            plant.death_date = timezone.now()
            plant.is_active = False
            plant.save()
            
            # Résoudre automatiquement les paris sur cette plante
            active_bets = Bet.objects.filter(plant=plant, is_resolved=False)
            for bet in active_bets:
                bet.resolve_bet()
            
            updated_count += 1
        
        messages.success(
            request, 
            f"{updated_count} plante(s) marquée(s) comme morte(s). {active_bets.count()} pari(s) résolu(s)."
        )
    
    mark_as_dead.short_description = "Marquer comme mortes (résout les paris)"
    
    def mark_as_alive(self, request, queryset):
        """
        Réactiver des plantes marquées comme mortes
        """
        updated_count = queryset.filter(is_active=False).update(
            is_active=True,
            death_date=None
        )
        
        messages.success(
            request, 
            f"{updated_count} plante(s) réactivée(s)."
        )
    
    mark_as_alive.short_description = "Réactiver les plantes"
    
    def recalculate_days_alive(self, request, queryset):
        """
        Recalcule les jours de vie (action factice pour l'exemple)
        """
        messages.info(
            request, 
            "Le calcul des jours de vie est automatique via la propriété du modèle."
        )
    
    recalculate_days_alive.short_description = "Recalculer jours de vie (info)"
    
    def days_alive_display(self, obj):
        """
        Affiche les jours de vie avec couleur selon l'état
        """
        days = obj.days_alive
        if obj.is_active:
            return format_html(
                '<span style="color: green; font-weight: bold;">{} jours</span>', 
                days
            )
        else:
            return format_html(
                '<span style="color: red;">{} jours (mort)</span>', 
                days
            )
    
    days_alive_display.short_description = 'Jours de vie'
    
    def image_preview(self, obj):
        """
        Miniature de l'image dans la liste
        """
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover;" />',
                obj.image.url
            )
        return "Aucune image"
    
    image_preview.short_description = 'Image'
    
    def image_preview_large(self, obj):
        """
        Grande prévisualisation dans le détail
        """
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 300px;" />',
                obj.image.url
            )
        return "Aucune image"
    
    image_preview_large.short_description = 'Aperçu'
    
    def get_queryset(self, request):
        """
        Optimisation des requêtes pour l'admin
        """
        return super().get_queryset(request).select_related('owner')

class CriterionAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'criterion_type', 'unit', 'is_active', 'description_short'
    ]
    list_filter = ['criterion_type', 'is_active']
    search_fields = ['name', 'description']
    list_editable = ['is_active']
    
    fieldsets = (
        ('Informations du critère', {
            'fields': ('name', 'criterion_type', 'description')
        }),
        ('Configuration', {
            'fields': ('unit', 'is_active')
        }),
    )
    
    actions = ['activate_criteria', 'deactivate_criteria']
    
    def activate_criteria(self, request, queryset):
        updated_count = queryset.update(is_active=True)
        messages.success(request, f"{updated_count} critère(s) activé(s).")
    
    def deactivate_criteria(self, request, queryset):
        updated_count = queryset.update(is_active=False)
        messages.success(request, f"{updated_count} critère(s) désactivé(s).")
    
    activate_criteria.short_description = "Activer les critères"
    deactivate_criteria.short_description = "Désactiver les critères"
    
    def description_short(self, obj):
        """
        Affiche une version raccourcie de la description
        """
        if len(obj.description) > 50:
            return obj.description[:50] + '...'
        return obj.description
    
    description_short.short_description = 'Description'

class PlantMeasurementAdmin(admin.ModelAdmin):
    list_display = [
        'plant', 'criterion', 'value', 'unit_display', 'measured_at'
    ]
    list_filter = ['criterion', 'measured_at', 'plant']
    search_fields = ['plant__name', 'criterion__name', 'notes']
    readonly_fields = ['measured_at']
    date_hierarchy = 'measured_at'
    
    def unit_display(self, obj):
        return obj.criterion.unit
    unit_display.short_description = 'Unité'
    
    def get_queryset(self, request):
        """
        Optimisation des requêtes pour l'admin
        """
        return super().get_queryset(request).select_related('plant', 'criterion')

admin.site.register(Plant, PlantAdmin)
admin.site.register(Criterion, CriterionAdmin)
admin.site.register(PlantMeasurement, PlantMeasurementAdmin)