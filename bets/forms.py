from django import forms
from .models import Bet
from django.utils import timezone

class BetForm(forms.ModelForm):
    class Meta:
        model = Bet
        fields = ['predicted_death_date', 'bet_amount']
        widgets = {
            'predicted_death_date': forms.DateTimeInput(
                attrs={
                    'type': 'date',  # Même avec DateTimeInput, vous pouvez utiliser type="date"
                    'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg',
                    'format': '%Y-%m-%d'  # Format d'affichage
                }
            ),
            'bet_amount': forms.NumberInput(
                attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg', 'placeholder': 'Votre mise'}
            ),
        }
    
    def __init__(self, *args, **kwargs):
        user_points = kwargs.pop('user_points', 0)
        super().__init__(*args, **kwargs)
        max_bet = min(500, user_points)
        self.fields['bet_amount'].widget.attrs.update({'min': 10, 'max': max_bet})
        
        # Forcer le format de date pour l'affichage
        self.fields['predicted_death_date'].input_formats = ['%Y-%m-%d']