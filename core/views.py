# ====================================
# 📦 IMPORTS
# ====================================
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.hashers import make_password

from .models import (
    Usuario, Nivel, Seccion, Material,
    Evaluacion, Pregunta, Respuesta,
    ResultadoEvaluacion, ProgresoUsuario
)
from .forms import (
    CustomUserCreationForm, CustomAuthenticationForm,
    LevelForm, SectionForm,
    UserEditForm, UserCreateForm
)

# ====================================
# 🔐 AUTENTICACIÓN DE USUARIOS
# ====================================

def custom_login(request):
    """Inicio de sesión personalizado"""
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'¡Bienvenido, {user.username}!')
            return redirect('admin_panel' if user.is_admin else 'user_dashboard')
        else:
            messages.error(request, 'Credenciales incorrectas.')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'core/login.html', {'form': form})

def custom_register(request):
    """Registro personalizado"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Cuenta creada con éxito.')
            return redirect('user_dashboard')
        else:
            messages.error(request, 'Error en el registro.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'core/register.html', {'form': form})

def custom_logout(request):
    """Cerrar sesión"""
    logout(request)
    return redirect('login')


# ====================================
# 👤 PANEL DE USUARIO
# ====================================

@login_required
def user_dashboard(request):
    """Vista principal del panel de usuario"""
    return render(request, 'core/user/dashboard.html')

@login_required
def user_learn(request):
    """Vista para aprender: lista de niveles"""
    niveles = Nivel.objects.order_by('orden')
    progreso = ProgresoUsuario.objects.filter(usuario=request.user)
    completados = {p.nivel_id: p.completado for p in progreso}
    return render(request, 'core/user/learn.html', {
        'niveles': niveles,
        'completados': completados
    })

@login_required
def ver_nivel(request, nivel_id):
    """Vista detallada de un nivel y sus secciones"""
    nivel = get_object_or_404(Nivel, id=nivel_id)
    secciones = nivel.secciones.prefetch_related('materiales')
    progreso, _ = ProgresoUsuario.objects.get_or_create(usuario=request.user, nivel=nivel)
    if request.method == 'POST':
        progreso.completado = True
        progreso.fecha_completado = timezone.now()
        progreso.save()
        siguiente = Nivel.objects.filter(orden=nivel.orden + 1).first()
        if siguiente:
            ProgresoUsuario.objects.get_or_create(usuario=request.user, nivel=siguiente)
        return redirect('learn')
    return render(request, 'core/view.html', {
        'nivel': nivel,
        'secciones': secciones,
        'progreso': progreso
    })


# ====================================
# 🧠 EVALUACIÓN Y RESULTADOS (USUARIO)
# ====================================

@login_required
def evaluation_view(request, nivel_id):
    """Mostrar evaluación, procesar respuestas y guardar resultado"""
    nivel = get_object_or_404(Nivel, id=nivel_id)
    evaluacion = get_object_or_404(Evaluacion, nivel=nivel)
    preguntas = evaluacion.preguntas.prefetch_related('respuestas')

    resultado_existente = ResultadoEvaluacion.objects.filter(usuario=request.user, evaluacion=evaluacion).first()
    if resultado_existente:
        return render(request, 'core/evaluation_score.html', {
            'resultado': resultado_existente,
            'evaluacion': evaluacion,
            'nivel': nivel
        })

    if request.method == 'POST':
        respuestas_usuario = request.POST
        puntaje = 0
        total = preguntas.count()
        for pregunta in preguntas:
            seleccion = respuestas_usuario.get(f"pregunta_{pregunta.id}")
            correcta = pregunta.respuestas.filter(es_correcta=True).first()
            if correcta and str(correcta.id) == seleccion:
                puntaje += 1
        porcentaje = int((puntaje / total) * 100)
        aprobado = porcentaje >= evaluacion.puntaje_minimo_aprobacion

        ResultadoEvaluacion.objects.create(
            usuario=request.user,
            evaluacion=evaluacion,
            puntaje_obtenido=porcentaje,
            aprobado=aprobado
        )

        if aprobado:
            progreso, _ = ProgresoUsuario.objects.get_or_create(usuario=request.user, nivel=nivel)
            progreso.completado = True
            progreso.fecha_completado = timezone.now()
            progreso.save()
            siguiente = Nivel.objects.filter(orden=nivel.orden + 1).first()
            if siguiente:
                ProgresoUsuario.objects.get_or_create(usuario=request.user, nivel=siguiente)

        return redirect('evaluation_view', nivel_id=nivel.id)

    return render(request, 'core/evaluation.html', {
        'evaluacion': evaluacion,
        'preguntas': preguntas,
        'nivel': nivel
    })

@login_required
def ver_resultado_evaluacion(request, resultado_id):
    """Mostrar resultado detallado de evaluación del usuario"""
    resultado = get_object_or_404(ResultadoEvaluacion, id=resultado_id, usuario=request.user)
    evaluacion = resultado.evaluacion
    preguntas = evaluacion.pregunta_set.all()
    respuestas_usuario = resultado.respuestas_usuario.all() if hasattr(resultado, 'respuestas_usuario') else []
    return render(request, 'core/admin/evaluation_page.html', {
        'resultado': resultado,
        'preguntas': preguntas,
        'respuestas_usuario': respuestas_usuario
    })


# ====================================
# 🛠️ PANEL DE ADMINISTRACIÓN
# ====================================

def es_admin(user):
    return user.is_authenticated and user.is_admin

@login_required
@user_passes_test(es_admin)
def admin_panel(request):
    """Vista principal del panel de administrador"""
    usuarios = Usuario.objects.filter(is_admin=False)
    niveles = Nivel.objects.all()
    resultados = ResultadoEvaluacion.objects.select_related('usuario', 'evaluacion')
    return render(request, 'core/admin/dashboard.html', {
        'usuarios': usuarios,
        'niveles': niveles,
        'resultados': resultados,
        'total_usuarios': usuarios.count(),
        'total_niveles': niveles.count(),
        'evaluaciones_totales': resultados.count()
    })

@login_required
@user_passes_test(es_admin)
def admin_evaluation_results(request):
    """Lista de resultados de evaluaciones"""
    resultados = ResultadoEvaluacion.objects.select_related('usuario', 'evaluacion').order_by('-fecha')
    return render(request, 'core/admin/evaluation_result.html', {
        'resultados': resultados
    })

@login_required
@user_passes_test(es_admin)
def admin_view_evaluation_result(request, resultado_id):
    """Vista detallada del resultado de evaluación de un usuario"""
    resultado = get_object_or_404(ResultadoEvaluacion, id=resultado_id)
    evaluacion = resultado.evaluacion
    usuario = resultado.usuario
    preguntas = evaluacion.preguntas.prefetch_related('respuestas')
    respuestas_usuario = {
        r.pregunta_id: r for r in resultado.respuestas_usuario.all()
    } if hasattr(resultado, 'respuestas_usuario') else {}

    return render(request, 'core/admin/evaluation_page.html', {
        'resultado': resultado,
        'usuario': usuario,
        'evaluacion': evaluacion,
        'preguntas': preguntas,
        'respuestas_usuario': respuestas_usuario
    })


# ====================================
# 👥 ADMINISTRACIÓN DE USUARIOS
# ====================================

@login_required
@user_passes_test(es_admin)
def admin_users_list(request):
    """Lista de usuarios normales"""
    usuarios = Usuario.objects.filter(is_admin=False)
    return render(request, 'core/admin/user.html', {'usuarios': usuarios})

@login_required
@user_passes_test(es_admin)
def admin_user_create(request):
    """Crear nuevo usuario"""
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.password = make_password(form.cleaned_data['password'])
            user.save()
            return redirect('admin_users')
    else:
        form = UserCreateForm()
    return render(request, 'core/admin/create.html', {'form': form})

@login_required
@user_passes_test(es_admin)
def admin_user_edit(request, user_id):
    """Editar un usuario existente"""
    usuario = get_object_or_404(Usuario, id=user_id)
    form = UserEditForm(request.POST or None, instance=usuario)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('admin_users')
    return render(request, 'core/admin/user_edit.html', {'form': form, 'usuario': usuario})

@login_required
@user_passes_test(es_admin)
def admin_user_toggle(request, user_id):
    """Activar o desactivar usuario"""
    user = get_object_or_404(Usuario, id=user_id)
    user.is_active = not user.is_active
    user.save()
    return redirect('admin_users')

@login_required
@user_passes_test(es_admin)
def admin_user_delete(request, user_id):
    """Eliminar usuario"""
    user = get_object_or_404(Usuario, id=user_id)
    user.delete()
    return redirect('admin_users')


# ====================================
# 📘 CRUD DE NIVELES Y SECCIONES
# ====================================

@login_required
@user_passes_test(es_admin)
def admin_levels_list(request):
    """Lista de niveles"""
    niveles = Nivel.objects.order_by('orden')
    return render(request, 'core/admin/levels.html', {'niveles': niveles})

@login_required
@user_passes_test(es_admin)
def admin_level_create(request):
    """Crear nuevo nivel"""
    if request.method == 'POST':
        form = LevelForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_levels')
    else:
        form = LevelForm()
    return render(request, 'core/admin/level_create.html', {'form': form})

@login_required
@user_passes_test(es_admin)
def admin_level_edit(request, level_id):
    """Editar nivel existente"""
    nivel = get_object_or_404(Nivel, id=level_id)
    form = LevelForm(request.POST or None, instance=nivel)
    if form.is_valid():
        form.save()
        return redirect('admin_levels')
    return render(request, 'core/admin/level_edit.html', {'form': form, 'nivel': nivel})

@login_required
@user_passes_test(es_admin)
def admin_level_delete(request, level_id):
    """Eliminar nivel"""
    nivel = get_object_or_404(Nivel, id=level_id)
    if request.method == 'POST':
        nivel.delete()
        return redirect('admin_levels')
    return render(request, 'core/admin/level_delete.html', {'nivel': nivel})

@login_required
@user_passes_test(es_admin)
def admin_level_sections(request, level_id):
    """Listar secciones de un nivel"""
    nivel = get_object_or_404(Nivel, id=level_id)
    secciones = nivel.secciones.all()
    return render(request, 'core/admin/section_list.html', {'nivel': nivel, 'secciones': secciones})

@login_required
@user_passes_test(es_admin)
def admin_section_create(request, level_id):
    """Crear nueva sección dentro de un nivel"""
    nivel = get_object_or_404(Nivel, id=level_id)
    if request.method == 'POST':
        form = SectionForm(request.POST)
        if form.is_valid():
            seccion = form.save(commit=False)
            seccion.nivel = nivel
            seccion.save()
            return redirect('admin_level_sections', level_id=nivel.id)
    else:
        form = SectionForm()
    return render(request, 'core/admin/section_form.html', {'form': form, 'nivel': nivel})
