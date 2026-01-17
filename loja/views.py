from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from .forms import ProdutoForm
from .models import Produto, ImagemProduto, Pedido, ItemPedido
from django.utils import timezone

def home(request):
    categoria_filter = request.GET.get('categoria') # Pega o ?categoria=da_url
    
    if categoria_filter == 'bebe':
        # Filtra meninos e meninas bebés
        produtos = Produto.objects.filter(categoria__in=['bebe_menino', 'bebe_menina'])
    elif categoria_filter:
        produtos = Produto.objects.filter(categoria=categoria_filter)
    else:
        produtos = Produto.objects.all()

    return render(request, 'home.html', {'produtos': produtos})

def ver_produto(request, id):
    produto = get_object_or_404(Produto, id=id)
    return render(request, 'detalhe_produto.html', {'produto': produto})

def registar_cliente(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Faz login automático após criar conta
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/registar.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # --- O SEGREDO DO REDIRECIONAMENTO ---
            if user.is_staff or user.is_superuser:
                return redirect('dashboard') # Admin vai para o Manager
            else:
                return redirect('home')      # Cliente vai para a Loja
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

# --- LÓGICA PRIVADA (MANAGER) ---

@login_required
def dashboard(request):
    # Segurança extra: só admins entram aqui
    if not request.user.is_staff:
        return redirect('home')
        
    produtos = Produto.objects.all()
    return render(request, 'dashboard.html', {'produtos': produtos})

@login_required
def gerir_produto(request, id=None):
    if not request.user.is_staff: return redirect('home')
    
    produto = get_object_or_404(Produto, id=id) if id else None
    
    if request.method == 'POST':
        form = ProdutoForm(request.POST, request.FILES, instance=produto)
        if form.is_valid():
            produto_salvo = form.save()
            
            # --- LÓGICA PARA GUARDAR AS IMAGENS EXTRA ---
            imagens = request.FILES.getlist('imagens_galeria')
            for f in imagens:
                ImagemProduto.objects.create(produto=produto_salvo, imagem=f)
            # --------------------------------------------

            return redirect('dashboard')
    else:
        form = ProdutoForm(instance=produto)
        
    titulo = "Editar" if id else "Novo Produto"
    return render(request, 'form_produto.html', {'form': form, 'titulo': titulo})

@login_required
def apagar_produto(request, id):
    if not request.user.is_staff: return redirect('home') # Proteção
    produto = get_object_or_404(Produto, id=id)
    produto.delete()
    return redirect('dashboard')

# 2. VER O CARRINHO
@login_required(login_url='login')
def carrinho(request):
    if request.user.is_authenticated:
        cliente = request.user
        pedido, criado = Pedido.objects.get_or_create(cliente=cliente, completo=False)
        itens = pedido.itempedido_set.all()
    else:
        itens = []
        pedido = {'get_total_carrinho': 0, 'get_itens_total': 0}

    context = {'itens': itens, 'pedido': pedido}
    return render(request, 'carrinho.html', context)

# 3. ADICIONAR AO CARRINHO
@login_required(login_url='login')
def adicionar_carrinho(request, produto_id):
    produto = Produto.objects.get(id=produto_id)
    pedido, criado = Pedido.objects.get_or_create(cliente=request.user, completo=False)
    
    item_pedido, criado = ItemPedido.objects.get_or_create(pedido=pedido, produto=produto)
    
    item_pedido.quantidade = (item_pedido.quantidade or 0) + 1
    item_pedido.save()
    
    return redirect('carrinho')

# 4. FINALIZAR COMPRA
@login_required
def checkout(request):
    pedido = Pedido.objects.get(cliente=request.user, completo=False)
    pedido.completo = True
    pedido.id_transacao = str(timezone.now().timestamp())
    pedido.save()
    return redirect('meus_pedidos')

# 5. MEUS PEDIDOS
@login_required
def meus_pedidos(request):
    pedidos = Pedido.objects.filter(cliente=request.user, completo=True).order_by('-data_pedido')
    return render(request, 'meus_pedidos.html', {'pedidos': pedidos})

@login_required
def dashboard(request):
    # Apenas Staff pode ver isto
    if not request.user.is_staff:
        return redirect('home')

    # 1. Buscar apenas encomendas finalizadas (pagas)
    pedidos_pagos = Pedido.objects.filter(completo=True).order_by('-data_pedido')
    
    # 2. Calcular Estatísticas
    total_faturado = sum(p.get_total_carrinho for p in pedidos_pagos)
    total_pedidos = pedidos_pagos.count()
    pedidos_pendentes = pedidos_pagos.filter(enviado=False).count()
    pedidos_enviados = pedidos_pagos.filter(enviado=True).count()
    
    # 3. Buscar os Produtos para a lista de gestão
    produtos = Produto.objects.all().order_by('-id')

    context = {
        'pedidos': pedidos_pagos, # Lista das encomendas
        'produtos': produtos,     # Lista dos produtos para editar
        'total_faturado': total_faturado,
        'total_pedidos': total_pedidos,
        'pedidos_pendentes': pedidos_pendentes,
        'pedidos_enviados': pedidos_enviados,
    }
    return render(request, 'dashboard.html', context)

# NOVA FUNÇÃO: Marcar encomenda como enviada
@login_required
def processar_pedido(request, id):
    if not request.user.is_staff: return redirect('home')
    
    pedido = Pedido.objects.get(id=id)
    pedido.enviado = not pedido.enviado # Inverte (Se false vira true, e vice-versa)
    pedido.save()
    
    return redirect('dashboard')