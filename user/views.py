from django.shortcuts import render
from django.http import JsonResponse
import json
import code
from . import models
import hashlib
import time
from django.conf import settings
from tools.jwt_self import Jwt
from tools.login_check import login_check

# Create your views here.

@login_check('PUT')
def users(request, username=None):
    if request.method == 'GET':
        # get user's data
        if username:
            try:
                user = models.user_profile.objects.get(username=username)
            except Exception as e:
                user = None
            if not user:
                result = {'code':208, 'error': 'no user'}
                return JsonResponse(result)
            if request.GET.keys():
                data = {}
                for key in request.GET.keys():
                    if hasattr(user, key):
                        value = getattr(user, key)
                        if key == 'avatar':
                            data[key] = str(value)
                        else:
                            data[key] = value
                result = {'code':200, 'username':username, 'data': data}
                return JsonResponse(result)
            else:
                result = {'code':200, 'username':username, 'data':{'nickname':user.nickname, 'info': user.info, 'sign': user.sign, 'avatar': str(user.avatar)}}
                return JsonResponse(result)
        else:
            return JsonResponse({'code':200})

    elif request.method == 'POST':
        # create user
        json_str = request.body
        if not json_str:
            result = {'code':201, 'error':'no any data'}
            return JsonResponse(result)
        json_obj = json.loads(json_str)
        username = json_obj.get('username')
        if not username:
            result = {'code':202, 'error':'no username'}
            return JsonResponse(result)
        email = json_obj.get('email')
        if not email:
            result = {'code':203, 'error':'no email'}
            return JsonResponse(result)
        password_1 = json_obj.get('password_1')
        password_2 = json_obj.get('password_2')
        if not password_1 or not password_2:
            result = {'code':204, 'error':'Please input your password'}
            return JsonResponse(result)
        if password_1 != password_2:
            result = {'code':205, 'error':'Input two different password'}
            return JsonResponse(result)
        # check if the username has been used
        if models.user_profile.objects.filter(username=username):
            result = {'code':206, 'error':'Username has been used'}
            return JsonResponse(result)      
        # password
        m = hashlib.md5()
        m.update(password_1.encode())
        # signature and info
        sign = info = ''
        # create new user in database
        try:
            models.user_profile.objects.create(username=username,nickname=username,email=email, password=m.hexdigest(), sign=sign, info=info)
        except Exception as e:
            # possible reasons: username has been used; database is down
            result = {'code':207, 'error':'Server is busy'}
            return JsonResponse(result)
        # make token
        token = Jwt.encode({'username':username})
        result = {'code':200, 'username':username, 'data':{'token':token.decode()}}
        return JsonResponse(result)
    
    elif request.method == 'PUT':
        # updata data
        json_str = request.body
        if not json_str:
            result = {'code':209, 'error':'no any data'}
            return JsonResponse(result)
        json_obj = json.loads(json_str)
        if 'sign' not in json_obj:
            result = {'code':210, 'error':'no signature'}
            return JsonResponse(result)
        if 'info' not in json_obj:
            result = {'code':211, 'error':'no infomation'}
            return JsonResponse(result)
        # update user's info
        sign = json_obj.get('sign')
        info = json_obj.get('info')
        nickname = json_obj.get('nickname')    
        request.user.sign = sign
        request.user.info = info
        request.user.nickname = nickname
        request.user.save()
        result = {'code': 200, 'username': request.user.username}
        return JsonResponse(result)

    else:
        raise

@login_check('POST')
def users_avatar(request, username):
    if request.method != 'POST':
        result = {'code':212, 'error': 'method should be post'}
        return JsonResponse(result)
    avatar = request.FILES.get('avatar')
    if not avatar:
        result = {'code': 213, 'error': 'do not have avatar'}
    request.user.avatar = avatar
    request.user.save()
    result = {'code':200, 'username':username}
    return JsonResponse(result)
