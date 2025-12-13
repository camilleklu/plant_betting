from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

# --- IMPORTS DES MODÈLES ---
from .models import Plant, PlantMeasurement
from bets.models import Bet
from leaderboard.models import UserScore

# --- IMPORTS DES FORMULAIRES ---
from .forms import PlantForm, MeasurementForm
from bets.forms import BetForm

@login_required
def plant_list(request):
    """ PAGE 1 : Liste de toutes les plantes actives """
    plants = Plant.objects.filter(is_active=True).order_by('-created_at')
    return render(request, 'plants/plant_list.html', {'plants': plants})

@login_required
def plant_detail(request, pk):
    """ PAGE 2 : Détail avec Logique Propriétaire (Gestion) vs Parieur (Jeu) """
    plant = get_object_or_404(Plant, pk=pk)
    is_owner = (plant.owner == request.user)
    
    # Récupération des données
    measurements = PlantMeasurement.objects.filter(plant=plant).order_by('-measured_at')
    
    # On récupère le score du visiteur actuel (pour le formulaire de pari)
    user_score, created = UserScore.objects.get_or_create(user=request.user)

    # Variables par défaut
    measurement_form = None
    bet_form = None
    user_has_bet = False

    # =================================================
    # === CAS A : C'EST LE PROPRIÉTAIRE (GESTION) ===
    # =================================================
    if is_owner:
        # 1. Gestion de l'ajout de mesure
        if request.method == 'POST' and 'add_measurement' in request.POST:
            measurement_form = MeasurementForm(request.POST)
            if measurement_form.is_valid():
                measure = measurement_form.save(commit=False)
                measure.plant = plant
                measure.save()
                messages.success(request, 'Statistique ajoutée !')
                return redirect('plant_detail', pk=pk)
        else:
            measurement_form = MeasurementForm()
            
        # 2. GESTION DE LA MORT (SIMPLIFIÉE GRÂCE À TON MODÈLE)
        if request.method == 'POST' and 'declare_death' in request.POST:
            death_date = timezone.now()
            
            # A. Marquer la plante comme morte
            plant.death_date = death_date
            plant.is_active = False
            plant.save()
            
            # B. Résoudre les paris en attente
            active_bets = Bet.objects.filter(plant=plant, is_resolved=False)
            count_winners = 0
            
            for bet in active_bets:
                # APPEL DE TA MÉTHODE DU MODÈLE BET
                # C'est elle qui calcule les points et met à jour le UserScore
                bet.resolve_bet()
                
                # On vérifie juste le résultat pour l'affichage du message
                if bet.won:
                    count_winners += 1
            
            messages.warning(request, f'Plante déclarée morte. {count_winners} pari(s) gagnant(s) ont été payés !')
            return redirect('plant_detail', pk=pk)

    # =================================================
    # === CAS B : C'EST UN PARIEUR (VISITEUR) ===
    # =================================================
    else:
        user_has_bet = Bet.objects.filter(user=request.user, plant=plant).exists()
        
        if request.method == 'POST' and 'place_bet' in request.POST:
            # On passe les points de l'user pour valider le max
            bet_form = BetForm(request.POST, user_points=user_score.total_points)
            
            if bet_form.is_valid():
                amount = bet_form.cleaned_data['bet_amount']
                
                # Vérification ultime du solde
                if user_score.total_points >= amount:
                    bet = bet_form.save(commit=False)
                    bet.user = request.user
                    bet.plant = plant
                    bet.save()
                    
                    # Débit immédiat de la mise
                    user_score.total_points -= amount
                    user_score.save()
                    
                    messages.success(request, 'Pari validé ! Bonne chance 🍀')
                    return redirect('plant_detail', pk=pk)
                else:
                    messages.error(request, 'Pas assez de points !')
            else:
                messages.error(request, 'Erreur dans le formulaire.')
        else:
            bet_form = BetForm(user_points=user_score.total_points)

    # Envoi au template
    context = {
        'plant': plant,
        'is_owner': is_owner,
        'measurements': measurements,
        'measurement_form': measurement_form,
        'bet_form': bet_form,
        'user_has_bet': user_has_bet,
        'user_points': user_score.total_points,
    }
    return render(request, 'plants/plant_detail.html', context)

@login_required
def add_plant(request):
    """ Page d'ajout de plante """
    if request.method == 'POST':
        form = PlantForm(request.POST, request.FILES)
        if form.is_valid():
            plant = form.save(commit=False)
            plant.owner = request.user
            plant.save()
            messages.success(request, 'Plante ajoutée avec succès !')
            return redirect('plant_detail', pk=plant.pk)
    else:
        form = PlantForm()
    return render(request, 'plants/add_plants.html', {'form': form})

@login_required
def add_measurement(request, plant_id):
    """ Vue alternative pour ajouter une mesure """
    plant = get_object_or_404(Plant, pk=plant_id)
    
    # Sécurité : seul le propriétaire peut ajouter des mesures
    if plant.owner != request.user:
        messages.error(request, "Vous n'êtes pas le propriétaire.")
        return redirect('plant_detail', pk=plant_id)

    if request.method == 'POST':
        form = MeasurementForm(request.POST)
        if form.is_valid():
            measurement = form.save(commit=False)
            measurement.plant = plant
            measurement.save()
            messages.success(request, 'Mesure ajoutée !')
            return redirect('plant_detail', pk=plant.pk)
    else:
        form = MeasurementForm()
    
    return render(request, 'plants/add_measurement.html', {'form': form, 'plant': plant})