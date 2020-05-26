from django.shortcuts import render
from django.http import JsonResponse
from tools.login_check import get_user_by_request, login_check
import json
from .models import Topic
from user.models import user_profile
import html
from message.models import Message

# Create your views here.

@login_check('POST', 'DELETE')
def topics(request, author_id):
    if request.method == 'GET':
        # get user's blog data
        # get the author
        authors = user_profile.objects.filter(username = author_id)
        if not authors:
            result = {'code':308, 'error': 'do not have any author'}
            return JsonResponse(result)
        author = authors[0]
        # get visitor
        visitor = get_user_by_request(request)
        visitor_name = None
        if visitor:
            visitor_name = visitor.username
        # get details
        t_id = request.GET.get('t_id')
        if t_id:
            # to check if is author self
            is_self = False
            t_id = int(t_id)
            if author_id == visitor_name:
                is_self = True
                try:
                    topic = Topic.objects.get(id = t_id)
                except Exception as e:
                    result = {'code':312, 'error': 'Sorry, the topic is not existing'}
                    return JsonResponse(result)
            else:
                try:
                    topic = Topic.objects.get(id = t_id, limit = 'public')
                except Exception as e:
                    result = {'code':313, 'error': 'Sorry, the topic is not existing!'}
                    return JsonResponse(result)
            result = get_topic_details(author, topic, is_self)
            return JsonResponse(result)
        #topics page 
        else:
            category = request.GET.get('category')
            if category in ['tec', 'no-tec']:
            # /v1/topics/<author_id>?category=[tec/no-tec]
                if author_id == visitor_name:
                    # if the visitor is author
                    topics = Topic.objects.filter(author = author_id, category = category)
                else:
                    # if the visitor is not author
                    topics = Topic.objects.filter(author = author_id, limit = 'public', category = category)
            else:
            # /v1/topics/<author_id>
                if author_id == visitor_name:
                    # if the visitor is author
                    topics = Topic.objects.filter(author = author_id)
                else:
                    # if the visitor is not author
                    topics = Topic.objects.filter(author = author_id, limit = 'public')
            result = make_topics_result(author, topics)
            return JsonResponse(result)

    elif request.method == 'POST':
        # create new article
        json_str = request.body
        if not json_str:
            result = {'code': 301, 'error': 'can not find any data'}
            return JsonResponse(result)
        json_obj = json.loads(json_str)
        title = json_obj.get('title')
        # xss transferred
        title = html.escape(title)
        # judge title
        if not title:
            result = {'code': 302, 'error': 'Please input the title of article'}
            return JsonResponse(result)
        category = json_obj.get('category')
        if category not in ['tec', 'no-tec']:
            result = {'code': 303, 'error': 'Please choose the category of article'}
            return JsonResponse(result)
        limit = json_obj.get('limit')
        if limit not in ['public', 'private']:
            result = {'code': 304, 'error': 'Please choose the limit of article'}
            return JsonResponse(result)
        content = json_obj.get('content')
        if not content:
            result = {'code': 305, 'error': 'Please input the content of article'}
            return JsonResponse(result)
        content_text = json_obj.get('content_text')
        if not content_text:
            result = {'code': 306, 'error': 'Please input the content_text of article'}
            return JsonResponse(result)
        introduce = content_text[:30]
        try:
            Topic.objects.create(
                title = title,
                category = category,
                limit = limit,
                introduce = introduce,
                content = content,
                author = request.user
            )
        except Exception as e:
            result = {'code': 307, 'error': 'Sorry, server is busy'}
            return JsonResponse(result)
        result = {'code':200, 'username': request.user.username}
        return JsonResponse(result)
    
    # delete specified topic
    elif request.method == 'DELETE':
        # get the user from token
        author = request.user
        token_author_id = author.username
        # user shold same as author
        if author_id != token_author_id:
            result = {'code':309, 'error': 'Please confirm if it is your blog'}
            return JsonResponse(result)
        topic_id = request.GET.get('topic_id')
        try:
            topic = Topic.objects.get(id = topic_id)
        except Exception as e:
            result = {'code':310, 'error': 'You can not do it'}
            return JsonResponse(result)
        if topic.author.username != author_id:
            result = {'code':311, 'error': 'You can not do it!'}
            return JsonResponse(result)
        topic.delete()
        return JsonResponse({'code':200})
    
    # other request
    else:
        result = {'code': 312, 'error': 'method of request is wrong'}
        return JsonResponse(result)


def make_topics_result(author, topics):
    result = {'code': 200, 'data': {}}
    data = {}
    data['nickname'] = author.nickname
    topics_list = []
    for topic in topics:
        d = {}
        d['id'] = topic.id
        d['title'] = topic.title
        d['category'] = topic.category
        d['introduce'] = topic.introduce
        d['author'] = author.username
        d['created_time'] = topic.created_time.strftime('%Y-%m-%d %H:%M:%S')
        topics_list.append(d)
    data['topics'] = topics_list
    result['data'] = data
    return result


def get_topic_details(author, topic, is_self):
    if is_self:
        # author self
        # get next topic
        next_topic = Topic.objects.filter(id__gt=topic.id, author=author).first()
        # get last topic
        last_topic = Topic.objects.filter(id__lt=topic.id, author=author).last()
    else:
        # visitor
        # get next topic
        next_topic = Topic.objects.filter(id__gt=topic.id, author=author, limit='public').first()
        # get last topic
        last_topic = Topic.objects.filter(id__lt=topic.id, author=author, limit='public').last()
    
    result = {'code': 200, 'data': {}}
    data = {}
    data['nickname'] = author.nickname
    data['title'] = topic.title
    data['category'] = topic.category
    data['created_time'] = topic.created_time.strftime('%Y-%m-%d %H:%M:%S')
    data['content'] = topic.content
    data['introduce'] = topic.introduce
    data['author'] = author.username
    if not next_topic:
        data['next_id'] = None
        data['next_title'] = None
    else:
        data['next_id'] = next_topic.id
        data['next_title'] = next_topic.title
    if not last_topic:
        data['last_id'] = None
        data['last_title'] = None
    else:
        data['last_id'] = last_topic.id
        data['last_title'] = last_topic.title
    data['messages_count'] = 0
    # get message from database
    messages = Message.objects.filter(topic_id = topic)
    msg_list = []
    reply_dict = {}
    for msg in messages:
        if msg.parent_message == 0:
            data['messages_count'] += 1
            message = {}
            message['id'] = msg.id
            message['content'] = msg.content
            message['publisher'] = msg.publisher_id.username
            message['publisher_avatar'] = str(msg.publisher_id.avatar)
            message['created_time'] = msg.created_time.strftime('%Y-%m-%d %H:%M:%S')
            msg_list.append(message)
        else:
            reply_dict.setdefault(msg.parent_message, [])
            reply = {}
            reply['publisher'] = msg.publisher_id.username
            reply['publisher_avatar'] = str(msg.publisher_id.avatar)
            reply['created_time'] = msg.created_time.strftime('%Y-%m-%d %H:%M:%S')
            reply['content'] = msg.content
            reply['msg_id'] = msg.id
            reply_dict[msg.parent_message].append(reply)
        for _msg in msg_list:
            if _msg['id'] in reply_dict:
                _msg['reply'] = reply_dict[_msg['id']]

    data['messages'] = msg_list
    
    result['data'] = data
    return result
    