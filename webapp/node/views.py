import pickle
import requests

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import redirect, render
from django.utils.safestring import mark_safe

from .forms import CreateNodeForm, CreateTransactionForm
from .models import Node


@login_required
def new_node(request):
    if request.method == "POST":
        form = CreateNodeForm(request.POST)
        if form.is_valid():
            IP = request.POST["IP"]
            PORT = request.POST["PORT"]
            nodes = Node.objects.filter(IP=IP, PORT=PORT)
            try:
                # For production add the timeout argument to ensure that the
                # request below won't stay hanging for a response.
                # e.g. requests.get(<address>, timeout=<time_in_seconds>)
                response = requests.get(f'http://{IP}:{PORT}/api/get_id')
                node_id = response.json()["message"]

                # Check if the node is already in our database
                nodes = Node.objects.filter(node_id=node_id, IP=IP, PORT=PORT)
                if nodes:
                    node = nodes[0]
                    node.status = "Online"
                else:
                    node = Node(node_id=node_id, IP=IP,
                                PORT=PORT, status="Online")

                node.save()
                messages.success(request, mark_safe(
                    f'Node {node_id} is online. <a target="_blank" '
                    f'href="/node/{node.id}/new-transaction"> Start Node </a>'
                    ))
                return redirect('node-new')
            except BaseException:
                # Change status to Offline
                for node in nodes:
                    node.status = "Offline"

                messages.error(request, 'The node is not currently online.')
                return redirect('node-new')
    else:
        form = CreateNodeForm()
    return render(request, 'node/node_form.html', {'form': form})


@login_required
def new_transaction(request, id):
    # There should be only one node satisfying the filtering statement below.
    nodes = Node.objects.filter(id=id, status="Online")
    if not nodes:
        messages.error(request, 'The node is not currently online.')
        return redirect('noobcash-home')

    # Getting the object from the queryset
    node = nodes[0]
    if request.method == "POST":
        form = CreateTransactionForm(request.POST)
        if form.is_valid():
            IP = node.IP
            PORT = node.PORT
            transaction = {
                "receiver": request.POST["receiver_id"],
                "amount": request.POST["amount"]
            }
            try:
                # For production add the timeout argument to ensure
                # that the request below won't stay hanging for a response.
                # e.g. requests.post(
                #                       <address>,
                #                       data=<data>,
                #                       timeout=<time_in_seconds>
                #                   )
                response = requests.post(
                    f'http://{IP}:{PORT}/api/create_transaction',
                    data=transaction)
                data = response.json()
                message = data["message"]
                try:
                    balance = data["balance"]
                    if response.status_code == 200:
                        messages.success(request, message)
                    else:
                        messages.error(request, message)
                    messages.info(
                        request, f'Your current balance is: {balance} NBCs')
                except KeyError:
                    messages.error(request, message)
            except BaseException:
                messages.error(
                    request, f'Node is not active. Try again later.')
            return redirect('node-new-transaction', node.id)
    else:
        form = CreateTransactionForm()
    return render(request, 'node/new_transaction.html',
                  {'form': form, 'node': node})


@login_required
def last_valid_transactions(request, id):
    nodes = Node.objects.filter(id=id, status="Online")
    if not nodes:
        messages.error(request, 'The node is not currently online.')
        return redirect('noobcash-home')

    node = nodes[0]

    try:
        # For production add the timeout argument to ensure that the
        # request below won't stay hanging for a response.
        # e.g. requests.get(<address>, timeout=<time_in_seconds>)
        response = requests.get(
            f'http://{node.IP}:{node.PORT}/api/get_transactions')
        data = pickle.loads(response._content)
        return render(request, 'node/last_valid_block.html',
                      {'node': node, 'transactions': data})
    except BaseException:
        pass

    return render(request, 'node/last_valid_block.html', {'node': node})


@login_required
def my_transactions(request, id):
    nodes = Node.objects.filter(id=id, status="Online")
    if not nodes:
        messages.error(request, 'The node is not currently online.')
        return redirect('noobcash-home')

    node = nodes[0]

    try:
        # For production add the timeout argument to ensure that the
        # request below won't stay hanging for a response.
        # e.g. requests.get(<address>, timeout=<time_in_seconds>)
        response = requests.get(
            f'http://{node.IP}:{node.PORT}/api/get_my_transactions')
        data = pickle.loads(response._content)

        paginator = Paginator(data, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, 'node/my_transactions.html',
                      {'node': node, 'page_obj': page_obj})
    except BaseException:
        pass

    return render(request, 'node/my_transactions.html', {'node': node})


@login_required
def my_balance(request, id):
    nodes = Node.objects.filter(id=id, status="Online")
    if not nodes:
        messages.error(request, "The node is not currently online")
        return redirect('noobcash-home')
    node = nodes[0]
    try:
        # For production add the timeout argument to ensure that the
        # request below won't stay hanging for a response.
        # e.g. requests.get(<address>, timeout=<time_in_seconds>)
        response = requests.get(
            f'http://{node.IP}:{node.PORT}/api/get_balance').json()
        balance = response['balance']
        return render(request, 'node/my_balance.html',
                      {'node': node, 'balance': balance})
    except BaseException:
        pass
    return render(request, 'node/my_balance.html', {'node': node})
