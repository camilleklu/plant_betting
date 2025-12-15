from django.db import models
from django.contrib.auth.models import User
from plants.models import Plant
from leaderboard.models import UserScore

class Bet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE)
    predicted_death_date = models.DateTimeField()
    bet_amount = models.IntegerField()
    bet_date = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)
    won = models.BooleanField(null=True, blank=True)
    points_won = models.IntegerField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.plant.name} - {self.bet_amount}pts"
    
    def calculate_points(self):
        """Calcule les points gagnés lorsque la plante meurt"""
        # Sécurité : On s'assure d'avoir la version la plus récente de la plante
        self.plant.refresh_from_db()
        
        if not self.plant.death_date:
            return 0
            
        # On compare les DATES (jours) uniquement, on ignore les heures/minutes
        # Cela évite les bugs de fuseaux horaires
        real_date = self.plant.death_date.date()
        pred_date = self.predicted_death_date.date()
        
        days_diff = abs((pred_date - real_date).days)
        
        if days_diff == 0:
            # Jour exact : x5
            return int(self.bet_amount * 5)
        elif days_diff <= 3:
            # Proche : x3
            return int(self.bet_amount * 3)
        elif days_diff <= 7:
            # Pas loin : x1.5
            return int(self.bet_amount * 1.5)
        else:
            return 0
    
    def resolve_bet(self):
        """Résout le pari lorsque la plante meurt"""
        # IMPORTANT : On rafraîchit les données pour être sûr de voir la mort
        self.plant.refresh_from_db()

        if self.plant.death_date and not self.is_resolved:
            self.points_won = self.calculate_points()
            self.won = self.points_won > 0
            self.is_resolved = True
            self.save()
            
            # Mettre à jour le score de l'utilisateur
            user_score, created = UserScore.objects.get_or_create(user=self.user)
            if self.won:
                user_score.total_points += self.points_won
                user_score.bets_won += 1
            else:
                user_score.bets_lost += 1
            
            user_score.calculate_accuracy()
            user_score.save()