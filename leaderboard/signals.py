from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from leaderboard.models import UserScore

@receiver(post_save, sender=User)
def create_user_score(sender, instance, created, **kwargs):
    if created:
        UserScore.objects.create(user=instance)

@receiver(post_save, sender=UserScore)
def update_all_ranks(sender, instance, **kwargs):
    """Met à jour tous les classements quand un score change"""
    scores = UserScore.objects.all().order_by('-total_points')
    for rank, score in enumerate(scores, 1):
        if score.rank != rank:
            score.rank = rank
            score.save()