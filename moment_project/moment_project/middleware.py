from datetime import timedelta
from django.utils.timezone import now

class UpdateLastSeenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.user.is_authenticated:
            profile = getattr(request.user, 'profile', None)
            if profile:
                if now() - profile.last_seen > timedelta(seconds=30):
                    profile.last_seen = now()
                    profile.save(update_fields=['last_seen'])
        return response
