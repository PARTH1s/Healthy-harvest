from unicodedata import name
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("schemes", views.schemes, name="schemes"),
    path("prices", views.prices, name="prices"),
    path("seasons", views.seasons, name = "seasons"),
    path('climate',views.climate,name="climate"),
	path('selectaverage',views.selectaverage,name="selectaverage"),
    path('stats',views.stats,name="stats"),
	path('selectlabel',views.selectlabel,name="selectlabel"),
    path("result", views.result, name = "result"),
    path("load", views.load, name = "load"),
    path("temp", views.temp, name="temp")
]

