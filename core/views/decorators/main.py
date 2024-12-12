from django.http import JsonResponse
from functools import wraps
from core.settings import common as settings

def secret_key_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        secret_key = request.headers.get('X-Secret-Key')
        if not secret_key or secret_key != settings.VIEWS_SECRET_KEY:
            return JsonResponse({'error': 'Unauthorized: Incorrect or Missing Secret Key'}, status=401)
        return view_func(request, *args, **kwargs)
    return _wrapped_view