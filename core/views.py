from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.models import User # <-- Nécessaire pour chercher l'email

# Imports de tes modèles
from plants.models import Plant
from bets.models import Bet
from leaderboard.models import UserScore

# Imports de tes formulaires
# Assure-toi d'importer le bon formulaire ici (CustomAuthenticationForm)
from .forms import CustomUserCreationForm, ProfileUpdateForm, CustomAuthenticationForm

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
            messages.success(request, "Inscription réussie ! Bienvenue.")
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'core/register.html', {'form': form})

# --- NOUVELLE LOGIQUE DE CONNEXION ---
def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            
            # 1. On cherche d'abord s'il existe un utilisateur avec cet email
            try:
                user_obj = User.objects.get(email=email)
                # 2. Si oui, on récupère son username pour l'authentification Django standard
                user = authenticate(username=user_obj.username, password=password)
                
                if user is not None:
                    login(request, user)
                    messages.success(request, f'Ravi de vous revoir, {user.username} !')
                    # Gestion de la redirection "next" (si l'utilisateur venait d'une page protégée)
                    next_url = request.POST.get('next') or request.GET.get('next')
                    return redirect(next_url if next_url else 'home')
                else:
                    messages.error(request, 'Mot de passe incorrect.')
            
            except User.DoesNotExist:
                messages.error(request, 'Aucun compte ne correspond à cet email.')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'core/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'Vous avez été déconnecté.')
    return redirect('home')

@login_required
def profile(request):
    # 1. Gestion des Scores
    try:
        user_score = UserScore.objects.get(user=request.user)
    except UserScore.DoesNotExist:
        user_score = UserScore.objects.create(user=request.user)
    
    # 2. Gestion des Paris
    active_bets = Bet.objects.filter(user=request.user, is_resolved=False)
    past_bets = Bet.objects.filter(user=request.user, is_resolved=True)

    # 3. Gestion des Plantes (CORRECTION ICI)
    # On utilise 'owner' car c'est le nom du champ dans ton models.py
    user_plants = Plant.objects.filter(owner=request.user)

    # 4. Gestion du Formulaire de Profil
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Votre profil a été mis à jour !')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    
    context = {
        'user_score': user_score,
        'active_bets': active_bets,
        'past_bets': past_bets,
        'user_plants': user_plants, # La variable contient maintenant les bonnes données
        'form': form,
    }
    return render(request, 'core/profile.html', context)

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
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


@login_required
def leaderboard(request):
    """ PAGE 3 : Le classement """
    # Les 50 meilleurs
    leaders = UserScore.objects.select_related('user').order_by('-total_points')[:50]
    
    # Rang de l'utilisateur actuel
    user_rank = 0
    try:
        current_score = UserScore.objects.get(user=request.user)
        user_rank = UserScore.objects.filter(total_points__gt=current_score.total_points).count() + 1
    except UserScore.DoesNotExist:
        pass

    return render(request, 'core/leaderboard.html', {
        'leaders': leaders,
        'user_rank': user_rank
    })