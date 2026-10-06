from django.urls import path

from . import views

app_name = 'business'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.DashboardLoginView.as_view(), name='login'),
    path('logout/', views.DashboardLogoutView.as_view(), name='logout'),

    path('proposals/', views.proposal_list, name='proposal_list'),
    path('proposals/new/', views.proposal_create, name='proposal_create'),
    path('proposals/<int:pk>/', views.proposal_detail, name='proposal_detail'),
    path('proposals/<int:pk>/edit/', views.proposal_edit, name='proposal_edit'),
    path('proposals/<int:pk>/status/', views.proposal_set_status, name='proposal_set_status'),
    path('proposals/<int:pk>/pdf/', views.proposal_pdf, name='proposal_pdf'),
    path('proposal/<int:pk>/send/', views.dashboard_send_proposal, name='send_proposal'),

    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoices/new/', views.invoice_create, name='invoice_create'),
    path('invoices/<int:pk>/', views.invoice_detail, name='invoice_detail'),
    path('invoices/<int:pk>/edit/', views.invoice_edit, name='invoice_edit'),
    path('invoices/<int:pk>/pdf/', views.invoice_pdf, name='invoice_pdf'),
    path('invoices/<int:pk>/payments/add/', views.payment_add, name='payment_add'),
    path('invoice/<int:pk>/send/', views.dashboard_send_invoice, name='send_invoice'),
    path('payments/<int:pk>/receipt/', views.receipt_pdf, name='receipt_pdf'),
    path('payments/<int:pk>/send/', views.payment_send_receipt, name='payment_send_receipt'),

    path('projects/', views.project_list, name='project_list'),
    path('projects/new/', views.project_create, name='project_create'),
    path('projects/<int:pk>/', views.project_detail, name='project_detail'),
    path('projects/<int:pk>/edit/', views.project_edit, name='project_edit'),
    path('projects/<int:pk>/status/', views.project_set_status, name='project_set_status'),

    path('clients/', views.client_list, name='client_list'),
    path('clients/new/', views.client_create, name='client_create'),
    path('clients/<int:pk>/edit/', views.client_edit, name='client_edit'),

    path('enquiries/', views.enquiry_list, name='enquiry_list'),
    path('enquiries/<int:pk>/done/', views.enquiry_mark_processed, name='enquiry_done'),
    path('enquiries/<int:pk>/to-client/', views.enquiry_to_client, name='enquiry_to_client'),
]
