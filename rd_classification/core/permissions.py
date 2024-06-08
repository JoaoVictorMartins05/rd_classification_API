from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_staff

class IsMedico(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.pessoa.is_medico

class IsSecretario(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.pessoais_secretario

class IsPaciente(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.pessoa.is_paciente
