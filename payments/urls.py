"""
URLs for Payments app.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('upload/<slug:course_slug>/', views.upload_payment_view, name='upload_payment'),
    path('status/<int:payment_id>/', views.payment_status_view, name='payment_status'),
    path('my/', views.my_payments_view, name='my_payments'),
]
