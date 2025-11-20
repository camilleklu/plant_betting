from django import forms
from .models import Plant, PlantMeasurement

class PlantForm(forms.ModelForm):
    class Meta:
        model = Plant
        fields = ['name', 'species', 'category', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'species': forms.TextInput(attrs={'class': 'form-input'}),
            'category': forms.TextInput(attrs={'class': 'form-input'}),
        }

class MeasurementForm(forms.ModelForm):
    class Meta:
        model = PlantMeasurement
        fields = ['criterion', 'value', 'notes']
        widgets = {
            'value': forms.NumberInput(attrs={'class': 'form-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3}),
        }