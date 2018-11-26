from django.urls import path
# from .views import *
from . import views
from . import feeds
urlpatterns=[
    path('',views.index,name="index"),
    # path('test/',views.test,name="test"),
    path('book/<int:bid>/',views.bookDetailView,name="book_detail"),
    path('accounts/login/',views.user_login,name="login"),
    path('accounts/logout/',views.user_logout,name="logout"),
    path('accounts/register/',views.signup,name='register'),
    path('checkout/',views.checkout,name="checkout"),
    path('payment/',views.paymentView,name="payment"),
    path('issued/',views.issuedView,name='issued'),
    path('shop/',views.catalogView,name="catalog"),
    path('profile/',views.profileView,name="profile"),
    path('uploaded/',views.uploadedView,name="uploaded"),
    path('feed/',feeds.HighestRatedFeed(),name="feed"),
    path('upload/',views.addBookView,name="book_upload"),
]