import base64
import json
import time
import copy
import hmac
from django.conf import settings


class Jwt():

    def __init__(self):
        pass

    @staticmethod
    def b64encode(content):
        return base64.urlsafe_b64encode(content).replace(b'=',b'')
    
    @staticmethod
    def b64decode(bytes):
        n = 4 - len(bytes) % 4
        bytes += b'=' * n
        return base64.urlsafe_b64decode(bytes)

    @staticmethod
    def encode(payload, key = settings.SECRET_KEY, exp=3600*24):
        # init hearer
        header = {'alg':'HS256', 'typ': 'JWT'}
        header_json = json.dumps(header, separators=(',',':'), sort_keys=True)
        header_bs = Jwt.b64encode(header_json.encode())
        # init payload
        payload_self = copy.deepcopy(payload)
        if not isinstance(exp, int) and not isinstance(exp, str):
            raise TypeError('expiration should be number!!')
        payload_self['exp'] = time.time() + int(exp)
        payload_json = json.dumps(payload_self, separators=(',',':'), sort_keys=True)
        payload_bs = Jwt.b64encode(payload_json.encode())
        # init signature
        if isinstance(key, str):
            key = key.encode()
        hm = hmac.new(key, header_bs + b'.' + payload_bs, digestmod='SHA256')
        sign_bs = Jwt.b64encode(hm.digest())
        
        return header_bs + b'.' + payload_bs + b'.' + sign_bs

    @staticmethod
    def decode(token, key = settings.SECRET_KEY):
        # verify signature
        header_bs, payload_bs, sign_bs = token.split(b'.')
        if isinstance(key, str):
            key = key.encode()
        hm = hmac.new(key, header_bs + b'.' + payload_bs, digestmod='SHA256')
        sign_verify = Jwt.b64encode(hm.digest())
        if sign_bs != sign_verify:
            raise
        # check if the pyload is expried
        payload_json = Jwt.b64decode(payload_bs)
        payload = json.loads(payload_json.decode())
        if 'exp' in payload:
            if payload['exp'] < time.time():
                raise
            return payload


        
