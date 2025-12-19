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
        self.plant.refresh_from_db()
        
        if not self.plant.death_date:
            return 0
            
        real_date = self.plant.death_date.date()
        pred_date = self.predicted_death_date.date()
        
        days_diff = abs((pred_date - real_date).days)
        
        # Jackpot : 0 ou 1 jour d'écart (pour absorber le décalage horaire)
        if days_diff <= 1:
            return int(self.bet_amount * 5)
            
        # Proche : 2 à 3 jours
        elif days_diff <= 3:
            return int(self.bet_amount * 3)
            
        # Pas loin : 4 à 7 jours
        elif days_diff <= 7:
            return int(self.bet_amount * 1.5)
            
        else:
            return 0
    
    def resolve_bet(self):
        """Résout le pari lorsque la plante meurt"""
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