from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_staff

class IsMedico(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.pessoa.is_medico

class IsSecretario(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.pessoa.is_secretario

class IsPaciente(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.pessoa.is_paciente

class CanDoExams(BasePermission):
    def has_permission(self, request, view):
        return request.user and (request.user.pessoa.is_medico or request.user.is_staff)
