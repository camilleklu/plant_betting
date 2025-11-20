from django.contrib import admin
from .models import Bet
from django.utils import timezone
from django.contrib import messages

class BetAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'plant', 'bet_amount', 'predicted_death_date', 
        'is_resolved', 'won', 'points_won', 'bet_date'
    ]
    list_filter = [
        'is_resolved', 'won', 'bet_date', 'user', 'plant'
    ]
    search_fields = [
        'user__username', 'plant__name', 'plant__species'
    ]
    readonly_fields = ['bet_date', 'points_won']
    list_per_page = 20
    date_hierarchy = 'bet_date'
    
    fieldsets = (
        ('Informations du pari', {
            'fields': ('user', 'plant', 'bet_amount', 'bet_date')
        }),
        ('Prédiction', {
            'fields': ('predicted_death_date',)
        }),
        ('Résolution', {
            'fields': ('is_resolved', 'won', 'points_won')
        }),
    )
    
    actions = ['force_resolve_bets', 'cancel_bets']
    
    def force_resolve_bets(self, request, queryset):
        """
        Action admin pour forcer la résolution de paris sélectionnés
        """
        resolved_count = 0
        for bet in queryset.filter(is_resolved=False):
            if bet.plant.death_date:
                bet.resolve_bet()
                resolved_count += 1
            else:
                messages.warning(
                    request, 
                    f"Le pari {bet.id} ne peut pas être résolu: la plante n'a pas de date de mort."
                )
        
        if resolved_count > 0:
            messages.success(
                request, 
                f"{resolved_count} pari(s) résolu(s) avec succès."
            )
    
    force_resolve_bets.short_description = "Résoudre les paris sélectionnés"
    
    def cancel_bets(self, request, queryset):
        """
        Action admin pour annuler des paris et rembourser les points
        """
        from leaderboard.models import UserScore
        
        cancelled_count = 0
        for bet in queryset.filter(is_resolved=False):
            try:
                user_score = UserScore.objects.get(user=bet.user)
                user_score.total_points += bet.bet_amount
                user_score.save()
                bet.delete()
                cancelled_count += 1
            except UserScore.DoesNotExist:
                messages.error(
                    request, 
                    f"Erreur avec le pari {bet.id}: score utilisateur non trouvé."
                )
        
        messages.success(
            request, 
            f"{cancelled_count} pari(s) annulé(s) et points remboursés."
        )
    
    cancel_bets.short_description = "Annuler les paris sélectionnés (remboursement)"
    
    def get_queryset(self, request):
        """
        Optimisation des requêtes pour l'admin
        """
        return super().get_queryset(request).select_related('user', 'plant')
    
    def days_until_prediction(self, obj):
        """
        Colonne calculée: jours restants jusqu'à la prédiction
        """
        if obj.predicted_death_date:
            delta = obj.predicted_death_date - timezone.now()
            return delta.days
        return "-"
    
    days_until_prediction.short_description = "Jours restants"

admin.site.register(Bet, BetAdmin)