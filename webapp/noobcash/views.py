import requests
from threading import Thread

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from node.models import Node


@login_required
def home(request):
    nodes = Node.objects.all()

    def thread_func(node):
        try:
            # For production add the timeout argument to ensure that the
            # request below won't stay hanging for a response.
            # e.g. requests.get(<address>, timeout=<time_in_seconds>)
            response = requests.get(f'http://{node.IP}:{node.PORT}/api/get_id')
            node.status = 'Online'
        except BaseException:
            node.status = 'Offline'
        node.save()

    # We use threads to optimize our TTFB (time to first byte).
    threads = []
    for node in nodes:
        thread = Thread(target=thread_func, args=(node,))
        threads.append(thread)
        thread.start()

    for tr in threads:
        tr.join()

    # We initialize our database by adding 10 default nodes. Therefore their
    # id will be less than 11 [0,...,10]
    return render(request, 'noobcash/homepage.html', {
        'nodes': Node.objects.filter(id__lt=11)
        }
    )
