from django.urls import path

from . import views

urlpatterns = [
    path('new/', views.new_node, name='node-new'),
    path(
        '<int:id>/new-transaction/',
        views.new_transaction,
        name='node-new-transaction'
    ),
    path(
        '<int:id>/last-valid-block/',
        views.last_valid_transactions,
        name='node-last-valid-block'
    ),
    path(
        '<int:id>/my-transactions/',
        views.my_transactions,
        name='node-my-transactions'
    ),
    path('<int:id>/my-balance/', views.my_balance, name='node-my-balance'),
]
