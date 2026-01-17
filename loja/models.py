from django.db import models
from django.contrib.auth.models import User
class Produto(models.Model):
    TIPO_OPCOES = [
        ('bebe_menino', 'Bebé Menino 👶💙'),
        ('bebe_menina', 'Bebé Menina 👶🩷'),
        ('rapaz', 'Rapaz 👦'),
        ('rapariga', 'Rapariga 👧'),
    ]

    nome = models.CharField(max_length=200)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.CharField(max_length=20, choices=TIPO_OPCOES, default='rapaz')
    
    # Campo de Idade / Tamanho
    idade = models.CharField(max_length=50, help_text="Ex: 3-6 Meses, 4 Anos")
    
    # Descrição Manual
    descricao = models.TextField(blank=True, null=True, help_text="Detalhes do produto")
    
    # Imagem Principal (Capa)
    imagem = models.ImageField(upload_to='produtos/', null=True, blank=True)
    
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome

# --- CLASSE NOVA PARA A GALERIA DE IMAGENS ---
# Isto permite adicionar várias fotos ao mesmo produto
class ImagemProduto(models.Model):
    produto = models.ForeignKey(Produto, related_name='imagens_extra', on_delete=models.CASCADE)
    imagem = models.ImageField(upload_to='produtos/galeria/')

    def __str__(self):
        return f"Imagem extra de {self.produto.nome}"


class Pedido(models.Model):
    cliente = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    data_pedido = models.DateTimeField(auto_now_add=True)
    completo = models.BooleanField(default=False)
    id_transacao = models.CharField(max_length=100, null=True)
    
    # NOVO CAMPO: Para saberes se já enviaste o pacote
    enviado = models.BooleanField(default=False)

    def __str__(self):
        return f"Pedido {self.id}"

    @property
    def get_total_carrinho(self):
        itens = self.itempedido_set.all()
        total = sum([item.get_total for item in itens])
        return total

    @property
    def get_itens_total(self):
        itens = self.itempedido_set.all()
        total = sum([item.quantidade for item in itens])
        return total

class ItemPedido(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.SET_NULL, null=True)
    pedido = models.ForeignKey(Pedido, on_delete=models.SET_NULL, null=True)
    quantidade = models.IntegerField(default=0, null=True, blank=True)
    data_adicionada = models.DateTimeField(auto_now_add=True)

    @property
    def get_total(self):
        return self.produto.preco * self.quantidade