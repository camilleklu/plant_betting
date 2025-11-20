from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from .models import UserProfile
from .models import ActivityLog


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Crée automatiquement un profil utilisateur quand un nouvel utilisateur est créé
    """
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Sauvegarde le profil utilisateur quand l'utilisateur est sauvegardé
    """
    try:
        instance.userprofile.save()
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def log_user_registration(sender, instance, created, **kwargs):
    """
    Log l'inscription d'un nouvel utilisateur
    """
    if created:
        ActivityLog.objects.create(
            activity_type='user_registered',
            user=instance,
            description=f"Nouvel utilisateur inscrit: {instance.username}"
        )