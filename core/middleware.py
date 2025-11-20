from django.shortcuts import redirect
from django.urls import reverse

class AuthRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Liste des URLs qui nécessitent une authentification
        auth_required_urls = [
            '/profile/',
            '/plants/add/',
            '/bets/create/',
            # Ajoutez d'autres URLs protégées ici
        ]
        
        if any(request.path.startswith(url) for url in auth_required_urls):
            if not request.user.is_authenticated:
                return redirect(f"{reverse('login')}?next={request.path}")
        
        response = self.get_response(request)
        return response