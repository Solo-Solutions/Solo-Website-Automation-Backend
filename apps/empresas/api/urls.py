from django.urls import path
from . import views


urlpatterns = [
    path('', views.api_overview, name='api_overview'),
    
    path('list-empresas/', views.get_list_empresas, name='list_empresas'),
    path('create-empresa/', views.create_empresa, name='create_empresa'),
    path('update-empresa/<uuid:id>', views.update_empresa, name='update-empresa'),
    path('delete-by-name/', views.delete_empresa_by_name, name='delete_empresa_by_name'),
]