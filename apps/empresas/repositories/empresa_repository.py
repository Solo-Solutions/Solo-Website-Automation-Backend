from apps.empresas.models import Empresa
from rest_framework.exceptions import ValidationError


class EmpresaRepository:
    def get_by_id(self, empresa_id):
        try:
            return Empresa.objects.get(id=empresa_id)
        except Empresa.DoesNotExist:
            return None
    
    def get_empresas(self):
        return Empresa.objects.all().order_by('-created_at')

    def validate_nome(self, empresa_id, nome):
        return Empresa.objects.exclude(id=empresa_id).filter(nome=nome).exists()
    
    def validate_cnpj(self, empresa_id, cnpj):
        return Empresa.objects.exclude(id=empresa_id).filter(cnpj=cnpj).exists()

    def update(self, empresa_id, **kwargs):
        empresa = self.get_by_id(empresa_id)

        if not empresa:
            raise ValidationError('Empresa não encontrada.')
        
        automacoes = kwargs.pop('automacoes', None)

        for key, value in kwargs.items():
            setattr(empresa, key, value)
        empresa.save()

        if automacoes is not None:
            empresa.automacoes.set(automacoes)

        return empresa