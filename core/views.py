from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from plants.models import Plant
from bets.models import Bet
from leaderboard.models import UserScore

def home(request):
    active_plants = Plant.objects.filter(is_active=True).order_by('-created_at')[:6]
    total_plants = Plant.objects.count()
    active_bets = Bet.objects.filter(is_resolved=False).count()
    
    context = {
        'active_plants': active_plants,
        'total_plants': total_plants,
        'active_bets': active_bets,
    }
    return render(request, 'core/home.html', context)

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Compte créé avec succès!')
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'core/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Bienvenue {username}!')
                return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'Vous avez été déconnecté.')
    return redirect('home')

@login_required
def profile(request):
    user_score = UserScore.objects.get(user=request.user)
    active_bets = Bet.objects.filter(user=request.user, is_resolved=False)
    past_bets = Bet.objects.filter(user=request.user, is_resolved=True)
    
    context = {
        'user_score': user_score,
        'active_bets': active_bets,
        'past_bets': past_bets,
    }
    return render(request, 'core/profile.html', context)

def rules(request):
    return render(request, 'core/rules.html')