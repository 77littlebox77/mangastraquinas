from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from loja import views # Importa as nossas views novas

urlpatterns = [
    path('admin_django/', admin.site.urls), # Mudei para não conflituar
    
    # LOJA
    path('', views.home, name='home'),
    path('produto/<int:id>/', views.ver_produto, name='ver_produto'),
    
    # CARRINHO E PEDIDOS (NOVOS)
    path('carrinho/', views.carrinho, name='carrinho'),
    path('adicionar_carrinho/<int:produto_id>/', views.adicionar_carrinho, name='adicionar_carrinho'),
    path('checkout/', views.checkout, name='checkout'),
    path('meus_pedidos/', views.meus_pedidos, name='meus_pedidos'),

    # Autenticação Personalizada
    path('login/', views.login_view, name='login'), # O nosso login inteligente
    path('registar/', views.registar_cliente, name='registar'), # Criar conta
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),

    # Loja Pública
    path('', views.home, name='home'),
    path('produto/<int:id>/', views.ver_produto, name='ver_produto'),
    
    # Área Manager
    path('manager/', views.dashboard, name='dashboard'),
    path('manager/novo/', views.gerir_produto, name='criar_produto'),
    path('manager/editar/<int:id>/', views.gerir_produto, name='editar_produto'),
    path('manager/apagar/<int:id>/', views.apagar_produto, name='apagar_produto'),
    path('manager/', views.dashboard, name='dashboard'),
    path('processar_pedido/<int:id>/', views.processar_pedido, name='processar_pedido'), # NOVO
    ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)