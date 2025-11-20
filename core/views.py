from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from plants.models import Plant
from bets.models import Bet
from leaderboard.models import UserScore
from .forms import CustomUserCreationForm

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
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Compte créé avec succès!')
            return redirect('home')
    else:
        form = CustomUserCreationForm()
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
    try:
        user_score = UserScore.objects.get(user=request.user)
    except UserScore.DoesNotExist:
        # Créer le UserScore s'il n'existe pas
        user_score = UserScore.objects.create(user=request.user)
    
    active_bets = Bet.objects.filter(user=request.user, is_resolved=False)
    past_bets = Bet.objects.filter(user=request.user, is_resolved=True)
    
    context = {
        'user_score': user_score,
        'active_bets': active_bets,
        'past_bets': past_bets,
    }
    return render(request, 'core/profile.html', context)

@login_required
def change_password(request):
    """
    Vue pour changer le mot de passe de l'utilisateur connecté
    """
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Mettre à jour la session pour éviter la déconnexion
            update_session_auth_hash(request, user)
            messages.success(request, 'Votre mot de passe a été changé avec succès!')
            return redirect('profile')
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'core/change_password.html', {'form': form})

def rules(request):
    return render(request, 'core/rules.html')