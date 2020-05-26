from django.db import models
from topic.models import Topic
from user.models import user_profile

# Create your models here.

class Message(models.Model):
    content = models.CharField('content', max_length=50)
    created_time = models.DateTimeField('created time', auto_now=False, auto_now_add=True)
    parent_message = models.IntegerField('parent message', default=0)
    publisher_id = models.ForeignKey(user_profile, verbose_name='id of publisher', on_delete=models.CASCADE)
    topic_id = models.ForeignKey(Topic, verbose_name='id of topic', on_delete=models.CASCADE)


    class Meta:
        db_table = 'message'