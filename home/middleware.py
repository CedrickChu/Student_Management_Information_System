from django.shortcuts import redirect
from django.urls import reverse

class RedirectNonStaffMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Check if user is authenticated and not a staff member
        if request.user.is_authenticated and not request.user.is_superuser:
            return redirect(reverse('custom-page'))  # Redirect to your custom page

        return response