# ====================================
# 🌐 URLS - Rutas de la aplicación
# ====================================

from django.urls import path
from . import views

urlpatterns = [

    # ============================
    # 🔐 AUTENTICACIÓN
    # ============================
    path('login/', views.custom_login, name='login'),
    path('register/', views.custom_register, name='register'),
    path('logout/', views.custom_logout, name='logout'),

    # ============================
    # 👤 PANEL DE USUARIO
    # ============================
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('dashboard/learn/', views.user_learn, name='learn'),
    path('dashboard/learn/nivel/<int:nivel_id>/', views.ver_nivel, name='ver_nivel'),
    path('dashboard/learn/nivel/<int:nivel_id>/evaluacion/', views.evaluation_view, name='evaluation_view'),

    # ============================
    # 🛠️ PANEL DE ADMINISTRADOR
    # ============================
    path('admin-panel/', views.admin_panel, name='admin_panel'),

    # Evaluaciones
    path('admin-panel/resultados/', views.admin_evaluation_results, name='admin_evaluation_results'),
    path('admin-panel/resultado/<int:resultado_id>/', views.admin_view_evaluation_result, name='admin_view_evaluation_result'),

    # Gestión de usuarios
    path('admin-panel/users/', views.admin_users_list, name='admin_users'),
    path('admin-panel/users/create/', views.admin_user_create, name='admin_user_create'),
    path('admin-panel/users/<int:user_id>/edit/', views.admin_user_edit, name='admin_user_edit'),
    path('admin-panel/users/<int:user_id>/toggle/', views.admin_user_toggle, name='admin_user_toggle'),
    path('admin-panel/users/<int:user_id>/delete/', views.admin_user_delete, name='admin_user_delete'),

    # Gestión de niveles y secciones
    path('admin-panel/levels/', views.admin_levels_list, name='admin_levels'),
    path('admin-panel/levels/create/', views.admin_level_create, name='admin_level_create'),
    path('admin-panel/levels/<int:level_id>/edit/', views.admin_level_edit, name='admin_level_edit'),
    path('admin-panel/levels/<int:level_id>/delete/', views.admin_level_delete, name='admin_level_delete'),
    path('admin-panel/levels/<int:level_id>/sections/', views.admin_level_sections, name='admin_level_sections'),
    path('admin-panel/levels/<int:level_id>/sections/create/', views.admin_section_create, name='admin_section_create'),
]
