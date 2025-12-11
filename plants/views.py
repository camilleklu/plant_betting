from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Plant, PlantMeasurement, Criterion
from .forms import PlantForm, MeasurementForm

@login_required
def plant_list(request):
    plants = Plant.objects.filter(is_active=True).order_by('-created_at')
    return render(request, 'plants/plant_list.html', {'plants': plants})

@login_required
def plant_detail(request, pk):
    plant = get_object_or_404(Plant, pk=pk)
    measurements = PlantMeasurement.objects.filter(plant=plant)
    active_bets = plant.bet_set.filter(is_resolved=False)
    
    # Vérifier si l'utilisateur a déjà parié sur cette plante
    user_has_bet = active_bets.filter(user=request.user).exists()
    
    context = {
        'plant': plant,
        'measurements': measurements,
        'active_bets': active_bets,
        'user_has_bet': user_has_bet,
    }
    return render(request, 'plants/plant_detail.html', context)

@login_required
def add_plant(request):
    if request.method == 'POST':
        form = PlantForm(request.POST, request.FILES)
        if form.is_valid():
            plant = form.save(commit=False)
            plant.owner = request.user
            plant.save()
            messages.success(request, 'Plante ajoutée avec succès!')
            return redirect('plant_detail', pk=plant.pk)
    else:
        form = PlantForm()
    return render(request, 'plants/add_plants.html', {'form': form})

@login_required
def add_measurement(request, plant_id):
    plant = get_object_or_404(Plant, pk=plant_id)
    
    if request.method == 'POST':
        form = MeasurementForm(request.POST)
        if form.is_valid():
            measurement = form.save(commit=False)
            measurement.plant = plant
            measurement.save()
            messages.success(request, 'Mesure ajoutée avec succès!')
            return redirect('plant_detail', pk=plant.pk)
    else:
        form = MeasurementForm()
    
    return render(request, 'plants/add_measurement.html', {
        'form': form,
        'plant': plant
    })