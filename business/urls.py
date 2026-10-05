from django.urls import path

from . import views

app_name = 'business'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('proposal/<int:pk>/send/', views.dashboard_send_proposal, name='send_proposal'),
    path('invoice/<int:pk>/send/', views.dashboard_send_invoice, name='send_invoice'),
]
