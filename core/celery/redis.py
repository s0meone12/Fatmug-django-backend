import redis
from django.conf import settings
redis_client = redis.Redis(host=settings.REDIS_HOST,port=int(settings.REDIS_PORT),password=settings.REDIS_PASSWORD,db=0)
