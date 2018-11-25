from django.urls import path
# from .views import *
from . import views
urlpatterns=[
    path('',views.index,name="index"),
    path('book/<int:bid>/',views.bookDetailView,name="book_detail"),
]