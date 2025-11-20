from django.contrib import admin
from .models import UserScore
from django.db.models import F
from django.contrib import messages

class UserScoreAdmin(admin.ModelAdmin):
    list_display = [
        'rank', 'user', 'total_points', 'bets_won', 'bets_lost', 
        'accuracy_rate', 'last_updated'
    ]
    list_display_links = ['user']
    list_filter = ['last_updated']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['last_updated', 'accuracy_rate']
    list_per_page = 25
    ordering = ['rank']
    
    fieldsets = (
        ('Utilisateur', {
            'fields': ('user',)
        }),
        ('Statistiques', {
            'fields': (
                'total_points', 'bets_won', 'bets_lost', 'accuracy_rate'
            )
        }),
        ('Classement', {
            'fields': ('rank', 'last_updated')
        }),
    )
    
    actions = ['recalculate_accuracy', 'reset_points', 'update_all_ranks']
    
    def recalculate_accuracy(self, request, queryset):
        """
        Recalcule le taux de précision pour les scores sélectionnés
        """
        for score in queryset:
            score.calculate_accuracy()
            score.save()
        
        messages.success(
            request, 
            f"Taux de précision recalculé pour {queryset.count()} utilisateur(s)."
        )
    
    recalculate_accuracy.short_description = "Recalculer le taux de précision"
    
    def reset_points(self, request, queryset):
        """
        Réinitialise les points des utilisateurs sélectionnés
        """
        from core.models import SiteSettings
        site_settings = SiteSettings.get_instance()
        
        updated_count = queryset.update(
            total_points=site_settings.starting_points,
            bets_won=0,
            bets_lost=0,
            accuracy_rate=0.0
        )
        
        # Mettre à jour les rangs
        self.update_all_ranks(request, UserScore.objects.all())
        
        messages.success(
            request, 
            f"{updated_count} utilisateur(s) réinitialisé(s) avec {site_settings.starting_points} points."
        )
    
    reset_points.short_description = "Réinitialiser les points (départ)"
    
    def update_all_ranks(self, request, queryset):
        """
        Met à jour tous les classements
        """
        # Cette action fonctionne sur tout le queryset, pas seulement la sélection
        scores = UserScore.objects.all().order_by('-total_points')
        for rank, score in enumerate(scores, 1):
            if score.rank != rank:
                score.rank = rank
                score.save()
        
        messages.success(request, "Tous les classements ont été mis à jour.")
    
    update_all_ranks.short_description = "Mettre à jour TOUS les classements"
    
    def get_queryset(self, request):
        """
        Optimisation des requêtes pour l'admin
        """
        return super().get_queryset(request).select_related('user')
    
    def get_actions(self, request):
        """
        Personnalise les actions disponibles
        """
        actions = super().get_actions(request)
        return actions

admin.site.register(UserScore, UserScoreAdmin)