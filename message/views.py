from django.shortcuts import render
from django.http import JsonResponse
from tools.login_check import login_check
import json
from topic.models import Topic
from message.models import Message

# Create your views here.
@login_check('POST')
def messages(request, topic_id):
    if request.method == 'POST':
        # announce message or reply mes.
        user = request.user
        json_str = request.body
        if not json_str:
            result = {'code':402, 'error': 'Do not have data'}
            return JsonResponse(result)
        json_obj = json.loads(json_str)
        content = json_obj.get('content')
        if not content:
            result = {'code': 403, 'error': 'Please input content'}
            return JsonResponse(result)
        parent_id = json_obj.get('parent_id', 0)
        # check if the topic is existing
        try:
            topic = Topic.objects.get(id = topic_id)
        except Exception as e:
            result = {'code': 404, 'error': 'Do not have topic'}
            return JsonResponse(result)
        # private
        if topic.limit == 'private':
            # check the visitor name
            if user.username != topic.author:
                result = {'code':405, 'error': 'You do not have the right!'}
                return JsonResponse(result)
        # create data
        Message.objects.create(content = content, publisher_id = user, topic_id = topic, parent_message = parent_id)
        return JsonResponse({'code':200, 'data':{}})



    else:
        result = {'code':401, 'error': 'Server can not accept this method of request'}
        return JsonResponse(result)