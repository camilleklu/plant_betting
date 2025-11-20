from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from plants.models import Plant
from .models import Bet
from .forms import BetForm
from leaderboard.models import UserScore

@login_required
def create_bet(request, plant_id):
    plant = get_object_or_404(Plant, pk=plant_id, is_active=True)
    user_score = UserScore.objects.get(user=request.user)
    
    # Vérifier si l'utilisateur a déjà parié sur cette plante
    existing_bet = Bet.objects.filter(user=request.user, plant=plant, is_resolved=False)
    if existing_bet.exists():
        messages.warning(request, 'Vous avez déjà un pari actif sur cette plante.')
        return redirect('plant_detail', pk=plant.pk)
    
    if request.method == 'POST':
        form = BetForm(request.POST, user_points=user_score.total_points)
        if form.is_valid():
            bet = form.save(commit=False)
            bet.user = request.user
            bet.plant = plant
            
            # Vérifier que l'utilisateur a assez de points
            if bet.bet_amount > user_score.total_points:
                messages.error(request, 'Vous n\'avez pas assez de points pour ce pari.')
                return render(request, 'bets/create_bet.html', {
                    'form': form,
                    'plant': plant,
                    'user_score': user_score
                })
            
            bet.save()
            
            # Déduire les points
            user_score.total_points -= bet.bet_amount
            user_score.save()
            
            messages.success(request, f'Pari placé avec succès! {bet.bet_amount} points engagés.')
            return redirect('plant_detail', pk=plant.pk)
    else:
        form = BetForm(user_points=user_score.total_points)
    
    return render(request, 'bets/create_bet.html', {
        'form': form,
        'plant': plant,
        'user_score': user_score
    })