from django import forms
from .models import Produto, ImagemProduto

# Widget especial para permitir selecionar vários ficheiros
class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class ProdutoForm(forms.ModelForm):
    # Campo extra para upload de múltiplas imagens
    imagens_galeria = MultipleFileField(label='Galeria de Imagens (Selecione várias)', required=False)

    class Meta:
        model = Produto
        fields = ['nome', 'preco', 'categoria', 'idade', 'descricao', 'imagem']