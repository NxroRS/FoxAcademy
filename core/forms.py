# ====================================
# 📄 FORMULARIOS DEL SISTEMA
# ====================================
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Usuario, Nivel, Seccion


# ====================================
# 🔐 FORMULARIOS DE AUTENTICACIÓN
# ====================================

class CustomUserCreationForm(UserCreationForm):
    """Formulario personalizado de registro de usuarios"""
    email = forms.EmailField(required=True)

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'password1', 'password2']


class CustomAuthenticationForm(AuthenticationForm):
    """Formulario personalizado de login"""
    username = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Nombre de usuario'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Contraseña'
    }))


# ====================================
# 👥 FORMULARIOS DE USUARIO (ADMIN)
# ====================================

class UserEditForm(forms.ModelForm):
    """Formulario para editar usuarios existentes desde el panel admin"""
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'input'}),
            'email': forms.EmailInput(attrs={'class': 'input'}),
        }


class UserCreateForm(forms.ModelForm):
    """Formulario para crear nuevos usuarios desde el panel admin"""
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'password', 'is_active']


# ====================================
# 📘 FORMULARIOS DE NIVELES Y SECCIONES
# ====================================

class LevelForm(forms.ModelForm):
    """Formulario para crear/editar niveles"""
    class Meta:
        model = Nivel
        fields = ['titulo', 'descripcion', 'orden']


class SectionForm(forms.ModelForm):
    """Formulario para crear/editar secciones dentro de un nivel"""
    class Meta:
        model = Seccion
        fields = ['titulo', 'descripcion', 'orden']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'w-full border-gray-300 rounded'}),
            'descripcion': forms.Textarea(attrs={'class': 'w-full border-gray-300 rounded', 'rows': 3}),
            'orden': forms.NumberInput(attrs={'class': 'w-full border-gray-300 rounded'}),
        }
