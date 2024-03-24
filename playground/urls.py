from django.urls import path
from . import views


url_patterns = [
  path('hello', views.say_hello),
]