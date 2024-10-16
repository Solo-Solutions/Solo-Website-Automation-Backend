from rest_framework.permissions import BasePermission


class IsSoloAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='solo_admin').exists()
    
class IsAdminEmpresa(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='resp_empresa').exists()
    
class CanCreateUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('accounts.add_user')
    
class CanDeleteUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('accounts.delete_user')