import cv2
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from classification.classification import executar

from .permissions import IsAdmin, IsMedico
from .models import User, Paciente, Medico, Secretario, Exame, Pessoa
from .serializers import UserSerializer, PacienteSerializer, MedicoSerializer, SecretarioSerializer, ExameSerializer, PessoaSerializer
from rest_framework import serializers
import SimpleITK as sitk


class PacienteViewSet(viewsets.ModelViewSet):
    queryset = Paciente.objects.all()
    serializer_class = PacienteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Paciente.objects.all()
        elif user.pessoa.is_paciente:
            return Paciente.objects.filter(pessoa=user.pessoa)
        elif user.pessoa.is_medico:
            return Paciente.objects.filter(pessoa__in=Medico.objects.filter(pessoa__user=user).values('pessoa'))
        else:
            return Paciente.objects.none()

    def perform_create(self, serializer):
        serializer.save()


class MedicoViewSet(viewsets.ModelViewSet):
    queryset = Medico.objects.all()
    serializer_class = MedicoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Medico.objects.all()
        elif user.pessoa.is_medico:
            return Medico.objects.filter(pessoa__user=user)
        else:
            return Medico.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_superuser:
            serializer.save()
        else:
            raise serializers.ValidationError("Você não tem permissão para realizar esta ação.")

        
class SecretarioViewSet(viewsets.ModelViewSet):
    queryset = Secretario.objects.all()
    serializer_class = SecretarioSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Secretario.objects.all()
        elif user.pessoa.is_secretario:
            return Secretario.objects.filter(pessoa__user=user)
        else:
            return Secretario.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_superuser or user.pessoa.is_medico:
            serializer.save()
        else:
            raise serializers.ValidationError("Você não tem permissão para realizar esta ação.")


class ExameViewSet(viewsets.ViewSet): 
    permission_classes = [IsAuthenticated, IsMedico | IsAdmin]
    serializer_class = ExameSerializer

    def list(self, request):
        queryset = self.get_queryset(request)
        serializer = ExameSerializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self, request):
        user = request.user
        if user.is_superuser:
            return Exame.objects.all()
        elif user.pessoa.is_medico:
            return Exame.objects.filter(medico__pessoa__user=user)
        elif user.pessoa.is_secretario:
            return Exame.objects.filter(medico__pessoa__user=user.pessoa.medico.pessoa.user)
        elif user.pessoa.is_paciente:
            return Exame.objects.filter(paciente__pessoa__user=user)
        else:
            return Exame.objects.none()

    @action(detail=False, methods=['POST'])
    def classificar(self, request):
        
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        medico_id = serializer.validated_data.get('medico')
        paciente_id = serializer.validated_data.get('paciente')
        imagem = serializer.validated_data.get('imagem')
        tipo_exame = serializer.validated_data.get('tipo_exame')
        data_exame = serializer.validated_data.get('data_exame')

        # Buscar o médico e o paciente
        medico = Medico.objects.get(pk=medico_id)
        paciente = Paciente.objects.get(pk=paciente_id)

        resultado = executar(imagem)

        # Criar o exame
        exame = Exame.objects.create(
            medico=medico,
            paciente=paciente,
            imagem=imagem,
            tipo_exame=tipo_exame,
            data_exame=data_exame,
            resultado=resultado
        )

        return Response(ExameSerializer(exame).data, status=status.HTTP_201_CREATED)