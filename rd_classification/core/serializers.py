from rest_framework import serializers
from .models import User, Paciente, Medico, Secretario, Exame, Pessoa

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

class PessoaSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=True)

    class Meta:
        model = Pessoa
        fields = ('id', 'user', 'nome', 'data_nascimento', 'endereco', 'telefone', 'cpf', 'is_medico', 'is_secretario', 'is_paciente')
        extra_kwargs = {'is_medico': {'read_only': True}, 'is_secretario': {'read_only': True}, 'is_paciente': {'read_only': True}}  # Campos de tipo de Pessoa readonly
        
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = self.fields['user'].create(validated_data=user_data)
        pessoa = Pessoa.objects.create(user=user, **validated_data)
        return pessoa

class PacienteSerializer(serializers.ModelSerializer):
    pessoa = PessoaSerializer()

    class Meta:
        model = Paciente
        fields = ('id', 'pessoa')

    def create(self, validated_data):
        pessoa_data = validated_data.pop('pessoa')
        pessoa_data['is_paciente'] = True 
        pessoa = PessoaSerializer.create(PessoaSerializer(), validated_data=pessoa_data)
        paciente = Paciente.objects.create(pessoa=pessoa, **validated_data)
        return paciente

class MedicoSerializer(serializers.ModelSerializer):
    pessoa = PessoaSerializer()

    class Meta:
        model = Medico
        fields = ('id', 'pessoa', 'especialidade', 'crm')

    def create(self, validated_data):
        pessoa_data = validated_data.pop('pessoa')
        pessoa_data['is_medico'] = True 
        pessoa = PessoaSerializer.create(PessoaSerializer(), validated_data=pessoa_data)
        medico = Medico.objects.create(pessoa=pessoa, **validated_data)
        return medico

class SecretarioSerializer(serializers.ModelSerializer):
    pessoa = PessoaSerializer()
    medico_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Secretario
        fields = ('id', 'pessoa', 'medico_id')

    def create(self, validated_data):
        pessoa_data = validated_data.pop('pessoa')
        pessoa_data['is_secretario'] = True 
        pessoa = PessoaSerializer.create(PessoaSerializer(), validated_data=pessoa_data)
        
        medico_id = validated_data.pop('medico_id')
        try:
            medico = Medico.objects.get(id=medico_id)
        except Medico.DoesNotExist:
            raise serializers.ValidationError("Médico não encontrado.")

        secretario = Secretario.objects.create(pessoa=pessoa, medico=medico, **validated_data)
        return secretario
    
class ExameSerializer(serializers.ModelSerializer):
    paciente = serializers.IntegerField(write_only=True)
    medico = serializers.IntegerField(write_only=True)

    class Meta:
        model = Exame
        fields = ('id', 'paciente', 'medico', 'tipo_exame', 'data_exame', 'resultado', 'imagem')