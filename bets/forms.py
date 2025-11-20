from django import forms
from .models import Bet
from django.utils import timezone

class BetForm(forms.ModelForm):
    class Meta:
        model = Bet
        fields = ['predicted_death_date', 'bet_amount']
        widgets = {
            'predicted_death_date': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-input'}
            ),
            'bet_amount': forms.NumberInput(attrs={'class': 'form-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        user_points = kwargs.pop('user_points', 1000)
        super().__init__(*args, **kwargs)
        
        # Limiter la mise entre 10 et 500 points, ou le solde disponible
        max_bet = min(500, user_points)
        self.fields['bet_amount'].widget.attrs.update({
            'min': 10,
            'max': max_bet,
            'step': 10
        })
    
    def clean_bet_amount(self):
        bet_amount = self.cleaned_data['bet_amount']
        if bet_amount < 10:
            raise forms.ValidationError("La mise minimum est de 10 points.")
        if bet_amount > 500:
            raise forms.ValidationError("La mise maximum est de 500 points.")
        return bet_amount
    
    def clean_predicted_death_date(self):
        death_date = self.cleaned_data['predicted_death_date']
        if death_date <= timezone.now():
            raise forms.ValidationError("La date de mort prédite doit être dans le futur.")
        return death_date