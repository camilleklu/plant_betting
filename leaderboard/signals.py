from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from leaderboard.models import UserScore
from django.utils import timezone


@receiver(post_save, sender=User)
def create_user_score(sender, instance, created, **kwargs):
    if created:
        UserScore.objects.create(user=instance)

@receiver(post_save, sender=UserScore)
def update_all_ranks(sender, instance, **kwargs):
    """
    Met à jour tous les classements quand un score change
    """
    # Éviter les appels récursifs
    if kwargs.get('raw', False):
        return
        
    scores = UserScore.objects.all().order_by('-total_points')
    for rank, score in enumerate(scores, 1):
        UserScore.objects.filter(id=score.id).update(rank=rank)