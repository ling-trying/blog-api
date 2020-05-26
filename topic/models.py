from django.db import models
from user.models import user_profile

# Create your models here.


# class Topic


class Topic(models.Model):
    title = models.CharField('article title', max_length=50)
    category = models.CharField('category of blog', max_length=20)
    limit = models.CharField('reading limit', max_length=10)
    introduce = models.CharField('introduce of article', max_length=90)
    content = models.TextField('content of article')
    created_time = models.DateTimeField('creating time of article', auto_now=False, auto_now_add=True)
    updated_time = models.DateTimeField('updating time of article', auto_now=True, auto_now_add=False)
    author = models.ForeignKey(user_profile, on_delete=models.CASCADE)

    class Meta:
        db_table = 'topic'
