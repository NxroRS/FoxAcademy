# ====================================
# 📦 MODELOS DEL SISTEMA DE APRENDIZAJE
# ====================================

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

# ====================================
# 👤 MODELO DE USUARIO PERSONALIZADO
# ====================================

class Usuario(AbstractUser):
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        return self.username


# ====================================
# 🧱 ESTRUCTURA DE CURSOS
# ====================================

class Nivel(models.Model):
    """Nivel o curso dentro del sistema. Tiene un orden y puede depender de otro nivel."""
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField()
    orden = models.PositiveIntegerField(unique=True)
    desbloqueado_por = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"Nivel {self.orden} - {self.titulo}"


class Seccion(models.Model):
    """Sección dentro de un nivel. Contiene uno o más materiales."""
    nivel = models.ForeignKey(Nivel, on_delete=models.CASCADE, related_name='secciones')
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField()
    orden = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['orden']

    def __str__(self):
        return f"{self.nivel.titulo} - {self.titulo}"


class Material(models.Model):
    """Material de aprendizaje dentro de una sección (texto, archivos, etc.)."""
    seccion = models.ForeignKey(Seccion, related_name='materiales', on_delete=models.CASCADE)
    titulo = models.CharField(max_length=100)
    contenido = models.TextField()  # Puede evolucionar a campo de tipo archivo/video/etc.

    def __str__(self):
        return f"{self.seccion} - {self.titulo}"


# ====================================
# 📊 PROGRESO DEL USUARIO
# ====================================

class ProgresoUsuario(models.Model):
    """Seguimiento del progreso por nivel del usuario."""
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    nivel = models.ForeignKey(Nivel, on_delete=models.CASCADE)
    completado = models.BooleanField(default=False)
    fecha_completado = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('usuario', 'nivel')

    def __str__(self):
        return f"{self.usuario.username} - Nivel {self.nivel.orden} - {'✅' if self.completado else '⏳'}"


# ====================================
# 🧠 EVALUACIÓN DEL NIVEL
# ====================================

class Evaluacion(models.Model):
    """Evaluación asociada a un único nivel."""
    nivel = models.OneToOneField('Nivel', on_delete=models.CASCADE, related_name='evaluacion')
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    intentos_maximos = models.PositiveIntegerField(default=3)
    puntaje_minimo_aprobacion = models.PositiveIntegerField(default=70)

    def __str__(self):
        return f"Evaluación de {self.nivel.titulo}"


class Pregunta(models.Model):
    """Pregunta dentro de una evaluación."""
    evaluacion = models.ForeignKey(Evaluacion, on_delete=models.CASCADE, related_name='preguntas')
    texto = models.TextField()

    def __str__(self):
        return f"Pregunta: {self.texto[:50]}..."


class Respuesta(models.Model):
    """Respuesta posible a una pregunta."""
    pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE, related_name='respuestas')
    texto = models.CharField(max_length=255)
    es_correcta = models.BooleanField(default=False)

    def __str__(self):
        return f"{'✅' if self.es_correcta else '❌'} {self.texto}"


class ResultadoEvaluacion(models.Model):
    """Resultado del usuario en una evaluación específica."""
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    evaluacion = models.ForeignKey(Evaluacion, on_delete=models.CASCADE)
    puntaje_obtenido = models.IntegerField()
    aprobado = models.BooleanField(default=False)
    fecha = models.DateTimeField(auto_now_add=True)
    respuestas_usuario = models.ManyToManyField('Respuesta', blank=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.evaluacion.nivel.titulo} - {self.puntaje_obtenido}%"
