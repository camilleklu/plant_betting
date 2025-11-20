from django.shortcuts import render
from .models import UserScore

def leaderboard(request):
    period = request.GET.get('period', 'all')
    
    scores = UserScore.objects.all()
    
    # Filtrer par période (simplifié)
    if period == 'week':
        # Implémenter la logique de filtrage par semaine
        pass
    elif period == 'month':
        # Implémenter la logique de filtrage par mois
        pass
    
    top_users = scores.order_by('-total_points')[:10]
    
    context = {
        'top_users': top_users,
        'period': period,
    }
    return render(request, 'leaderboard/leaderboard.html', context)