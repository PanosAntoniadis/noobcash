from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Node
from django.contrib import messages
from .forms import CreateNodeForm, CreateTransactionForm
from django.utils.safestring import mark_safe
import requests

@login_required
def new_node(request):
    if request.method == "POST":
        form = CreateNodeForm(request.POST)
        if form.is_valid():
            IP = request.POST["IP"]
            PORT = request.POST["PORT"]
            try:
                response = requests.get(f'http://{IP}:{PORT}/api/get_id')
                node_id = response.json()["message"]
                # ADD LINK TO NODE
                messages.success(request, mark_safe(f'Node {node_id} is online. <a href="#">Start Node</a>'))
                return redirect('node-new')
            except:
                messages.error(request, 'The node is not currently online.')
                return redirect('node-new')
    else:
        form = CreateNodeForm()
    return render(request, 'node/node_form.html', {'form': form})

@login_required
def new_transaction(request):
    if request.method == "POST":
        form = CreateTransactionForm(request.POST)
        if form.is_valid():
            # ADD REQUEST FOR TRANSACTION
            try:
                response = requests.get('')
                messages.success(request, f'The transaction was successful.')
                return redirect('node-balance')
            except:
                messages.error(request, f'Something went wrong. Please try again later.')
                return redirect('node-new-transaction')                            
    else:
        form = CreateTransactionForm()
    return render(request, 'node/new_transaction.html', {'form': form})

@login_required
def my_balance(request,id):
    nodes=Node.objects.filter(id=id,status="Online")
    if not nodes:
        messages.error(request,"The node is not currently online")
        return redirect('noobcash-home')
    node=nodes[0]
    try:
        response = requests.get(f'http://{node.IP}:{node.PORT}/api/get_balance').json()
        balance = response['balance']
        return render(request, 'node/my_balance.html', {'node': node,'balance':balance})
    except:
        pass
    return render(request, 'node/my_balance.html', {'node': node})

@login_required
def last_valid_transactions(request, id):
    nodes = Node.objects.filter(id=id, status="Online")
    if not nodes:
        messages.error(request, 'The node is not currently online.')
        return redirect('noobcash-home')
    
    node = nodes[0]

    try:
        response = requests.get(f'http://{node.IP}:{node.PORT}/api/get_transactions')
        data = pickle.loads(response._content)
        return render(request, 'node/last_valid_block.html', {'node':node, 'transactions':data})
    except:
        pass

    return render(request, 'node/last_valid_block.html', {'node':node})
    

@login_required
def my_transactions(request, id):
    nodes = Node.objects.filter(id=id, status="Online")
    if not nodes:
        messages.error(request, 'The node is not currently online.')
        return redirect('noobcash-home')
    
    node = nodes[0]

    try:
        response = requests.get(f'http://{node.IP}:{node.PORT}/api/get_my_transactions')
        data = pickle.loads(response._content)

        paginator = Paginator(data, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, 'node/my_transactions.html', {'node':node, 'page_obj':page_obj})
    except:
        pass

    return render(request, 'node/my_transactions.html', {'node':node})