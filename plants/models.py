from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Plant(models.Model):
    name = models.CharField(max_length=200)
    species = models.CharField(max_length=200)
    category = models.CharField(max_length=100)
    obtaining_date = models.DateTimeField(default=timezone.now)
    death_date = models.DateTimeField(null=True, blank=True)
    image = models.ImageField(upload_to='plants/')
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.species})"
    
    @property
    def days_alive(self):
        if self.death_date:
            return (self.death_date - self.obtaining_date).days
        return (timezone.now() - self.obtaining_date).days

class Criterion(models.Model):
    CRITERION_TYPES = [
        ('watering', 'Arrosage'),
        ('sunlight', 'Exposition soleil'),
        ('insects', 'Présence insectes'),
    ]
    
    name = models.CharField(max_length=100)
    criterion_type = models.CharField(max_length=50, choices=CRITERION_TYPES)
    description = models.TextField()
    unit = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class PlantMeasurement(models.Model):
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE)
    criterion = models.ForeignKey(Criterion, on_delete=models.CASCADE)
    value = models.FloatField()
    measured_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-measured_at']