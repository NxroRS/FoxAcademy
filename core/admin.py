from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    Usuario,
    Nivel, Seccion, Material,
    Evaluacion, Pregunta, Respuesta,
    ResultadoEvaluacion
)

# -----------------------------
# Usuario personalizado
# -----------------------------
@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    model = Usuario
    list_display = ['username', 'email', 'is_active', 'is_admin', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        ('Permisos personalizados', {'fields': ('is_admin',)}),
    )


# -----------------------------
# Admin de Material
# -----------------------------
@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'seccion']
    search_fields = ['titulo']
    list_filter = ['seccion__nivel']


# -----------------------------
# Sección con materiales inline
# -----------------------------
class MaterialInline(admin.TabularInline):
    model = Material
    extra = 1

@admin.register(Seccion)
class SeccionAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'nivel']
    inlines = [MaterialInline]
    search_fields = ['titulo']
    list_filter = ['nivel']


# -----------------------------
# Nivel con secciones inline
# -----------------------------
class SeccionInline(admin.StackedInline):
    model = Seccion
    extra = 1

@admin.register(Nivel)
class NivelAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'orden', 'descripcion']
    list_display_links = ['titulo']
    list_editable = ['orden']
    ordering = ['orden']
    inlines = [SeccionInline]
    search_fields = ['titulo']

# -----------------------------
# Pregunta con respuestas inline
# -----------------------------
class RespuestaInline(admin.TabularInline):
    model = Respuesta
    extra = 2

@admin.register(Pregunta)
class PreguntaAdmin(admin.ModelAdmin):
    inlines = [RespuestaInline]
    list_display = ['texto', 'evaluacion']
    search_fields = ['texto']
    list_filter = ['evaluacion']


# -----------------------------
# Evaluación con preguntas inline
# -----------------------------
class PreguntaInline(admin.StackedInline):
    model = Pregunta
    extra = 1

@admin.register(Evaluacion)
class EvaluacionAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'nivel', 'puntaje_minimo_aprobacion']
    inlines = [PreguntaInline]
    search_fields = ['titulo']
    list_filter = ['nivel']


# -----------------------------
# Resultados de evaluaciones
# -----------------------------
@admin.register(ResultadoEvaluacion)
class ResultadoEvaluacionAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'evaluacion', 'puntaje_obtenido', 'aprobado', 'fecha']
    list_filter = ['evaluacion', 'aprobado']
    search_fields = ['usuario__username', 'evaluacion__titulo']
