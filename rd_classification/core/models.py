from django.contrib.auth.models import User, Group, Permission
from django.db import models
from django.core.validators import RegexValidator

class Pessoa(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='pessoa')
    nome = models.CharField(max_length=255)
    data_nascimento = models.DateField(null=True, blank=True)
    endereco = models.CharField(max_length=255, null=True, blank=True)
    telefone = models.CharField(max_length=15, null=True, blank=True)
    cpf = models.CharField(max_length=11, 
                            #validators=[RegexValidator(r'^\d{3}\.\d{3}\.\d{3}-\d{2}$')], 
                            blank=True, 
                            null=True)
    is_medico = models.BooleanField(default=False)
    is_secretario = models.BooleanField(default=False)
    is_paciente = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if hasattr(self, 'medico'):
            self.is_medico = True
        if hasattr(self, 'secretario'):
            self.is_secretario = True
        if hasattr(self, 'paciente'):
            self.is_paciente = True
        super().save(*args, **kwargs)

class Medico(models.Model):
    pessoa = models.OneToOneField(Pessoa, on_delete=models.CASCADE, related_name='medico')
    especialidade = models.CharField(max_length=255)
    crm = models.CharField(max_length=20)

class Secretario(models.Model):
    pessoa = models.OneToOneField(Pessoa, on_delete=models.CASCADE, related_name='secretario')
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE)

class Paciente(models.Model):
    pessoa = models.OneToOneField(Pessoa, on_delete=models.CASCADE, related_name='paciente')

class Exame(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE)
    tipo_exame = models.CharField(max_length=255)
    data_exame = models.DateField()
    resultado = models.TextField(null=True, blank=True)
    imagem = models.ImageField(upload_to='exames/', null=True, blank=True)