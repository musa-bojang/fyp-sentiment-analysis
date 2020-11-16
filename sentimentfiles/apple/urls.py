#from django.conf.urls import url, include
from django.urls import path, include
from . import views

app_name = 'apple'
urlpatterns = [
    #url(r'^', views.home, name="home"),
    path('home/', views.home, name="home"),
    # path('', views.index, name="index"),
    path('newpage/',  views.new_page,  name="my_function"),
    path('register/',views.register, name="register"),
    path('user_login/',views.user_login, name="user_login"),
   
    
]

