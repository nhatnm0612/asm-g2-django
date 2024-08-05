from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login),
    path('signup/', views.sign_up),
    path('test_token/', views.test_token),
    path('change_password/', views.change_password)
]