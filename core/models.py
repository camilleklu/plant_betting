from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    """
    Modèle étendu pour les informations supplémentaires de l'utilisateur
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True, null=True, verbose_name="Biographie")
    location = models.CharField(max_length=100, blank=True, null=True, verbose_name="Localisation")
    birth_date = models.DateField(null=True, blank=True, verbose_name="Date de naissance")
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name="Avatar")
    email_notifications = models.BooleanField(default=True, verbose_name="Notifications par email")
    
    # Statistiques de jeu (pour éviter de toujours joindre avec UserScore)
    total_points_cache = models.IntegerField(default=1000, verbose_name="Points totaux")
    rank_cache = models.IntegerField(default=0, verbose_name="Classement")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Profil de {self.user.username}"
    
    @property
    def get_avatar_url(self):
        """Retourne l'URL de l'avatar ou une image par défaut"""
        if self.avatar:
            return self.avatar.url
        return "/static/images/default-avatar.png"
    
    def update_cache_from_scores(self):
        """Met à jour le cache avec les données de UserScore"""
        from leaderboard.models import UserScore
        try:
            user_score = UserScore.objects.get(user=self.user)
            self.total_points_cache = user_score.total_points
            self.rank_cache = user_score.rank
            self.save()
        except UserScore.DoesNotExist:
            pass

class SiteSettings(models.Model):
    """
    Modèle pour les paramètres globaux du site
    """
    site_name = models.CharField(max_length=100, default="Paris Plantes")
    site_description = models.TextField(default="Plateforme de paris sur la durée de vie des plantes")
    maintenance_mode = models.BooleanField(default=False, verbose_name="Mode maintenance")
    
    # Paramètres de jeu
    starting_points = models.IntegerField(default=1000, verbose_name="Points de départ")
    min_bet_amount = models.IntegerField(default=10, verbose_name="Mise minimum")
    max_bet_amount = models.IntegerField(default=500, verbose_name="Mise maximum")
    
    # Multiplicateurs de gains
    exact_multiplier = models.FloatField(default=5.0, verbose_name="Multiplicateur exact (±1 jour)")
    close_multiplier = models.FloatField(default=3.0, verbose_name="Multiplicateur proche (±3 jours)")
    approximate_multiplier = models.FloatField(default=1.5, verbose_name="Multiplicateur approximatif (±7 jours)")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Paramètres de {self.site_name}"
    
    def save(self, *args, **kwargs):
        """S'assure qu'il n'y a qu'une seule instance de SiteSettings"""
        if not self.pk and SiteSettings.objects.exists():
            # S'il existe déjà des paramètres, on les met à jour au lieu d'en créer de nouveaux
            existing = SiteSettings.objects.first()
            self.pk = existing.pk
        super().save(*args, **kwargs)
    
    @classmethod
    def get_instance(cls):
        """Retourne l'instance unique des paramètres du site"""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

class Notification(models.Model):
    """
    Système de notifications pour les utilisateurs
    """
    NOTIFICATION_TYPES = [
        ('bet_won', 'Pari gagné'),
        ('bet_lost', 'Pari perdu'),
        ('plant_died', 'Plante morte'),
        ('new_rank', 'Nouveau classement'),
        ('system', 'Message système'),
        ('reminder', 'Rappel'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    related_object_id = models.PositiveIntegerField(null=True, blank=True)  # ID de l'objet lié
    related_object_type = models.CharField(max_length=50, blank=True)  # Type de l'objet lié
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
    
    def mark_as_read(self):
        """Marque la notification comme lue"""
        self.is_read = True
        self.save()
    
    @classmethod
    def create_notification(cls, user, notification_type, title, message, related_object=None):
        """Méthode utilitaire pour créer une notification"""
        notification = cls(
            user=user,
            notification_type=notification_type,
            title=title,
            message=message
        )
        
        if related_object:
            notification.related_object_id = related_object.pk
            notification.related_object_type = related_object.__class__.__name__
        
        notification.save()
        return notification

class ActivityLog(models.Model):
    """
    Journal des activités importantes sur le site
    """
    ACTIVITY_TYPES = [
        ('user_registered', 'Utilisateur inscrit'),
        ('plant_added', 'Plante ajoutée'),
        ('bet_placed', 'Pari placé'),
        ('plant_died', 'Plante morte'),
        ('bet_resolved', 'Pari résolu'),
        ('rank_changed', 'Classement changé'),
    ]
    
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPES)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Journal d'activité"
        verbose_name_plural = "Journaux d'activité"
    
    def __str__(self):
        return f"{self.get_activity_type_display()} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

class FAQ(models.Model):
    """
    Questions fréquemment posées
    """
    question = models.CharField(max_length=255, verbose_name="Question")
    answer = models.TextField(verbose_name="Réponse")
    order = models.IntegerField(default=0, verbose_name="Ordre d'affichage")
    is_active = models.BooleanField(default=True, verbose_name="Active")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"
    
    def __str__(self):
        return self.question