from django.shortcuts import render
from django.http import JsonResponse
import json
import hashlib
from tools.jwt_self import Jwt
from user import models

# Create your views here.
def tokens(request):
    #login === create token
    if request.method != 'POST':
        result = {'code': 101, 'error': 'Please use POST'}
        return JsonResponse(result)
    
    json_str = request.body
    if not json_str:
        result = {'code':102, 'error':'no any data'}
        return JsonResponse(result)
    json_obj = json.loads(json_str)
    username = json_obj.get('username')
    if not username:
        result = {'code':103, 'error': 'Please input your username'}
        return JsonResponse(result)
    password = json_obj.get('password')
    if not password:
        result = {'code':104, 'error': 'Please input your password'}
        return JsonResponse(request)
    user = models.user_profile.objects.filter(username=username)
    if not user:
        result = {'code':105, 'error': 'Username or password is wrong!'}
        return JsonResponse(request)
    user = user[0]
    m = hashlib.md5()
    m.update(password.encode())
    password = m.hexdigest()
    if password != user.password:
        result = {'code':207, 'error':'Username or password is wrong!'}
        return JsonResponse(result)

    # make token
    token = Jwt.encode({'username':username})
    result = {'code':200, 'username':username, 'data':{'token':token.decode()}}
    return JsonResponse(result)
     