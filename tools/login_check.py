from django.http import JsonResponse
from tools.jwt_self import Jwt
from user.models import user_profile

def login_check(*methods):
    def _login_check(func):
        def wrapper(request, *args, **kwargs):
            # using request inspect token
            # if invalid, return JsonReponse()
            token  = request.META.get('HTTP_AUTHORIZATION')

            if request.method not in methods:
                return func(request, *args, **kwargs)
            if not token:
                result = {'code': 107, 'error': 'Please login'}
                return JsonResponse(result)
            try:
                payload = Jwt.decode(token.encode())
            except Exception as e:
                result = {'code': 108, 'error': 'Please login'}
                return JsonResponse(result)
            username = payload['username']
            try:
                user = user_profile.objects.get(username=username)
            except:
                user = None
            if not user:
                result = {'code': 109, 'error': 'No user'}
                return JsonResponse(result)
            # request.xxx could be used in whole progrem
            request.user = user
            return func(request, *args, **kwargs)
        return wrapper
    return _login_check

def get_user_by_request(request):
    # try to get user
    token = request.META.get('HTTP_AUTHORIZATION')
    if not token:
        return None
    try:
        payload = Jwt.decode(token.encode())
    except Exception as e:
        return None
    username = payload['username']
    try:
        user = user_profile.objects.get('username')
    except Exception as e:
        return None
    return user

