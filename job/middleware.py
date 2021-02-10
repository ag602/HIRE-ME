import datetime
from django.core.cache import cache
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from rest_framework import serializers
from .models import User

class ActiveUserMiddleware(MiddlewareMixin):

    def process_request(self, request):
        current_user = request.user
        if request.user.is_authenticated:
            now = datetime.datetime.now()
            cache.set('seen_%s' % (current_user.username), now,
                           settings.USER_LASTSEEN_TIMEOUT)


class UserSerializer(serializers.ModelSerializer):

    last_seen = serializers.SerializerMethodField()
    online = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'online']


    def get_last_seen(self, obj):
        last_seen = cache.get('seen_%s' % obj.username)
        print(last_seen)
        obj.last_seen = last_seen
        return last_seen

    def get_online(self, obj):
        if obj.last_seen:
            now = datetime.datetime.now()
            delta = datetime.timedelta(seconds=settings.USER_ONLINE_TIMEOUT)
            if now > obj.last_seen + delta:
                return False
            else:
                return True
        else:
            return False