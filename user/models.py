from django.db import models

# Create your models here.

# class -> UserProfole
# table name user_profile
# username, nickname, email, password, sign, info, avatar

class user_profile(models.Model):
    username = models.CharField('username' ,max_length=11, primary_key=True)
    nickname = models.CharField('nickname', max_length=30)
    email = models.EmailField('email', max_length=254, null=True)
    password = models.CharField('password', max_length=32)
    sign = models.CharField('personal sign', max_length=50)
    info = models.CharField('presonal description', max_length=150)
    avatar = models.ImageField(upload_to='avatar/', height_field=None, width_field=None, max_length=None)

    class Meta:
        db_table = 'user_profole'
    
