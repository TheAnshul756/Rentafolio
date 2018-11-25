from django.urls import path
# from .views import *
from . import views
urlpatterns=[
    path('',views.index,name="index"),
    path('test/',views.test,name="test"),
    path('book/<int:bid>/',views.bookDetailView,name="book_detail"),
    path('login/',views.user_login,name="login"),
    path('logout/',views.user_logout,name="logout"),
    path('register/',views.signup,name='register'),
    path('checkout/',views.checkout,name="checkout"),
    path('payment/',views.paymentView,name="payment"),
    path('issued/',views.issuedView,name='issued'),
]