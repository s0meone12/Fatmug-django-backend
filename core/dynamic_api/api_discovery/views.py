# views.py
from django.urls import get_resolver, URLPattern, URLResolver
from rest_framework.views import APIView
from rest_framework.response import Response

class ApiDiscoveryView(APIView):
    """
    API discovery endpoint providing an overview of all available endpoints, HTTP methods, 
    and descriptions for easy reference by clients.
    """
    def get(self, request, *args, **kwargs):
        url_resolver = get_resolver()
        endpoints = self._get_urls(url_resolver.url_patterns)
        return Response({"endpoints": endpoints})

    def _get_urls(self, patterns, base_path=''):
        urls = []
        for pattern in patterns:
            # For URL pattern objects with views
            if isinstance(pattern, URLPattern):
                # Retrieve HTTP methods and other information
                view_class = getattr(pattern.callback, 'cls', None)
                if view_class and hasattr(view_class, 'http_method_names'):
                    url_info = {
                        "path": base_path + pattern.pattern.describe(),
                        "methods": [method.upper() for method in view_class.http_method_names if method != 'options'],
                        "name": pattern.name,
                        "description": view_class.__doc__ or "No description available",
                    }
                    urls.append(url_info)
            # For URL resolver objects (e.g., namespaces or nested URLs)
            elif isinstance(pattern, URLResolver):
                nested_urls = self._get_urls(pattern.url_patterns, base_path + pattern.pattern.describe())
                urls.extend(nested_urls)
        return urls
