from django.db import models


class Node(models.Model):
    id = models.IntegerField(primary_key=True)
    node_id = models.IntegerField(null=True, blank=True)
    IP = models.GenericIPAddressField()
    PORT = models.IntegerField(default=5000)
    status = models.TextField(max_length=7, default='Offline')

    def __str__(self):
        return f'Node {self.node_id}'

    def get_absolute_url(self):
        return reverse('node-new-transaction')


class Transaction(models.Model):
    receiver_id = models.IntegerField()
    amount = models.IntegerField()

    def get_absolute_url(self):
        return reverse('node-balance')
