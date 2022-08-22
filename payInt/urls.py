from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
    path('', views.index, name='payInt'),
    path('register/', views.register, name='register'),
    path('items/', views.product_list, name='items'),
    path('employees/', views.employee_list, name='employees'),
    path('upload/', views.files_upload, name='upload'),
]
