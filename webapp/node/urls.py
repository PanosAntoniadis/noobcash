from django.urls import path
from . import views

urlpatterns = [
    path('new/', views.new_node , name='node-new'),
    path('new-transaction/', views.new_transaction, name='node-new-transaction'),
]