from django import forms

from .models import Node, Transaction


class CreateNodeForm(forms.ModelForm):

    class Meta:
        model = Node
        fields = ('IP', 'PORT')


class CreateTransactionForm(forms.ModelForm):

    class Meta:
        model = Transaction
        fields = ('receiver_id', 'amount')
