from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from ..decorators.main import secret_key_required
import json
from core.models import AmzSku
# views created for testing purposes


class AmzSkuPricingView:

    @staticmethod
    @csrf_exempt
    @require_http_methods(["POST"])
    @secret_key_required
    def get_recommendation(request):
        if request.method == "POST":
            asins = json.loads(request.body).get('asins', [])
            return JsonResponse(AmzSku.manager.view.get_price_recommendation(asins), safe=False)

    @staticmethod
    @csrf_exempt
    @require_http_methods(["POST"])
    @secret_key_required
    def publish(request):
        if request.method == "POST":
            asins = json.loads(request.body).get('asins', [])
            return JsonResponse(AmzSku.manager.view.publish_price(asins), safe=False)
