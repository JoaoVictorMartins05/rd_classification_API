from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Paciente, Medico, Secretario, Exame, Pessoa 

@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ('get_user_username', 'get_data_nascimento', 'get_endereco', 'get_telefone', 'get_cpf') 
    search_fields = ('pessoa__user__username', 'pessoa__nome', 'pessoa__cpf')
    
    def get_user_username(self, obj):
        return obj.pessoa.user.username
    get_user_username.short_description = 'Usuário'

    def get_data_nascimento(self, obj):
        return obj.pessoa.data_nascimento
    get_data_nascimento.short_description = 'Data Nascimento'

    def get_endereco(self, obj):
        return obj.pessoa.endereco
    get_endereco.short_description = 'Endereço'

    def get_telefone(self, obj):
        return obj.pessoa.telefone
    get_telefone.short_description = 'Telefone'

    def get_cpf(self, obj):
        return obj.pessoa.cpf
    get_cpf.short_description = 'CPF'
    
@admin.register(Medico)
class MedicoAdmin(admin.ModelAdmin):
    list_display = ('get_user_username', 'especialidade', 'crm')
    search_fields = ('pessoa__user__username', 'pessoa__nome', 'pessoa__cpf', 'especialidade', 'crm')
    
    def get_user_username(self, obj):
        return obj.pessoa.user.username
    get_user_username.short_description = 'Usuário'

@admin.register(Secretario)
class SecretarioAdmin(admin.ModelAdmin):
    list_display = ('get_user_username',)
    search_fields = ('pessoa__user__username', 'pessoa__nome', 'pessoa__cpf')

    def get_user_username(self, obj):
        return obj.pessoa.user.username
    get_user_username.short_description = 'Usuário'

@admin.register(Exame)
class ExameAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'medico', 'tipo_exame', 'data_exame', 'resultado')
    search_fields = ('paciente__pessoa__nome', 'medico__pessoa__nome', 'tipo_exame', 'data_exame')
    list_filter = ('data_exame', 'tipo_exame', 'medico')
    date_hierarchy = 'data_exame'

    def paciente_nome(self, obj):
        return obj.paciente.pessoa.nome
    paciente_nome.admin_order_field = 'paciente__pessoa__nome'
    paciente_nome.short_description = 'Paciente'

    def medico_nome(self, obj):
        return obj.medico.pessoa.nome
    medico_nome.admin_order_field = 'medico__pessoa__nome'
    medico_nome.short_description = 'Medico'

@admin.register(Pessoa)
class PessoaAdmin(admin.ModelAdmin):
    list_display = ('user', 'nome', 'data_nascimento', 'endereco', 'telefone', 'cpf')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email', 'nome', 'cpf')