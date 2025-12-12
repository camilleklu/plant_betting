from django import forms
from .models import Bet
from django.utils import timezone

class BetForm(forms.ModelForm):
    class Meta:
        model = Bet
        fields = ['predicted_death_date', 'bet_amount']
        widgets = {
            'predicted_death_date': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}
            ),
            'bet_amount': forms.NumberInput(
                attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg', 'placeholder': 'Votre mise'}
            ),
        }

    def __init__(self, *args, **kwargs):
        # On récupère les points de l'utilisateur passés par la vue
        user_points = kwargs.pop('user_points', 0)
        super().__init__(*args, **kwargs)
        # On limite la mise au max de points de l'utilisateur (plafond à 500)
        max_bet = min(500, user_points)
        self.fields['bet_amount'].widget.attrs.update({'min': 10, 'max': max_bet})