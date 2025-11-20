from django.db import models
from django.contrib.auth.models import User

class UserScore(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    total_points = models.IntegerField(default=1000)
    bets_won = models.IntegerField(default=0)
    bets_lost = models.IntegerField(default=0)
    accuracy_rate = models.FloatField(default=0.0)
    rank = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.total_points}pts"
    
    def calculate_accuracy(self):
        total_bets = self.bets_won + self.bets_lost
        if total_bets > 0:
            self.accuracy_rate = (self.bets_won / total_bets) * 100
        else:
            self.accuracy_rate = 0.0
    
    def update_rank(self):
        """Met à jour le classement de l'utilisateur"""
        scores = UserScore.objects.filter(total_points__gt=self.total_points)
        self.rank = scores.count() + 1
        self.save()
