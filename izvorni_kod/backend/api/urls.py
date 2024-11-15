from django.urls import path, include
from . import views

urlpatterns = [
    path('auth/register/', views.register, name='register'),
    path('auth/login/', views.login, name='login'),
    path('records/', views.record_list, name='record-list'),
    path('records/add/', views.record_create, name='record-create'),
    path('goldmine-conditions/', views.goldmine_condition_list, name='goldmine-condition-list'),
]