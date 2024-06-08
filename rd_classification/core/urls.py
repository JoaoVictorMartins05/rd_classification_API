from django.http import HttpResponse
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PacienteViewSet, MedicoViewSet, SecretarioViewSet, ExameViewSet
from rest_framework.authtoken import views

router = DefaultRouter()
router.register(r'pacientes', PacienteViewSet)
router.register(r'medicos', MedicoViewSet)
router.register(r'secretarios', SecretarioViewSet)
router.register(r'exames', ExameViewSet, basename='exames')

urlpatterns = [
    #path('token-auth/', views.ObtainAuthToken.as_view()),
    path('', include(router.urls)),
]