from django.conf.urls import url
from . import views

urlpatterns = [
    url('/(?P<topic_id>\d+)$', views.messages),
]
