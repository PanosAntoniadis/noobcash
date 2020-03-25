from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from node.models import Node
import requests
from threading import Thread

@login_required
def home(request):
    nodes = Node.objects.all()

    def thread_func(node):
        try:
            response = requests.get(f'http://{node.IP}:{node.PORT}/api/get_id')
            node.status = 'Online'
        except:
            node.status = 'Offline'
        node.save()

    threads = []
    for node in nodes:
        thread = Thread(target=thread_func, args=(node,))
        threads.append(thread)
        thread.start()
    
    for tr in threads:
            tr.join()

    return render(request,'noobcash/homepage.html', {'nodes': Node.objects.all()})