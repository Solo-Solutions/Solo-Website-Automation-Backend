from rest_framework.exceptions import ValidationError, NotFound
from apps.empresas.repositories.empresa_repository import EmpresaRepository


class EmpresaService:
    def __init__(self):
        self.repository = EmpresaRepository()

    def get_empresa(self, empresa_id):
        empresa = self.repository.get_by_id(empresa_id)

        if not empresa:
            raise NotFound('Empresa não encontrada.')
        return empresa

    def get_list_empresas(self):
        empresas = self.repository.get_empresas()

        if not empresas:
            raise NotFound('Nenhuma empresa cadastrada.')
        
        return empresas

    def update_empresa(self, empresa, **kwargs):
        self.validate_fields(empresa.id, **kwargs)
        return self.repository.update(empresa.id, **kwargs)
    
    @staticmethod
    def validate_fields(empresa_id, **kwargs):
        nome = kwargs.get('nome', None)
        cnpj = kwargs.get('cnpj', None)

        if nome and EmpresaRepository().validate_nome(empresa_id, nome):
            raise ValidationError('O nome informado já possui uma empresa cadastrada.')
        
        if cnpj and EmpresaRepository().validate_cnpj(empresa_id, cnpj):
            raise ValidationError('O CNPJ informado já possui uma empresa cadastrada.')