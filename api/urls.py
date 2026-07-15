from django.urls import path
from . import views

urlpatterns = [

    path(
        'records/',
        views.health_records,
        name='api_records'
    ),
    path(
    'records/<int:id>/',
    views.update_record,
    name='update_record_api'
    ),
    path(
    'records/delete/<int:id>/',
    views.delete_record,
    name='delete_record_api'
    ),
    path(
    'register/',
    views.register,
    name='register'
    ),
    path(
    'profile/',
    views.profile,
    name='profile'
    ),
    path(
    'change-password/',
    views.change_password,
    name='change_password'
    ),
    path(
    'logout/',
    views.logout,
    name='logout'
    ),

]