from django.contrib import admin
from django import forms
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Sede, Producto, Venta, DetalleVenta, Cliente

# Formulario personalizado para el modelo User


class UserAdminForm(forms.ModelForm):
    class Meta:
        model = User
        fields = '__all__'

    # Campo para la contraseña
    password = forms.CharField(widget=forms.PasswordInput, required=False)

    def save(self, commit=True):
        user = super().save(commit=False)
        # Si se proporciona una contraseña, encriptarla
        if self.cleaned_data.get('password'):
            user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

# Personalizar el admin para el modelo User


class UserAdmin(BaseUserAdmin):
    form = UserAdminForm
    list_display = ('username', 'first_name', 'last_name',
                    'role', 'sede', 'is_staff', 'is_superuser')
    list_filter = ('role', 'sede', 'is_staff', 'is_superuser')
    search_fields = ('username', 'first_name', 'last_name')
    ordering = ('username',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información Personal', {'fields': ('first_name', 'last_name', 'email', 'telefono')}),
        ('Permisos', {'fields': ('is_active', 'is_staff','is_superuser', 'groups', 'user_permissions')}),
        ('Información Adicional', {'fields': ('role', 'sede')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password', 'first_name', 'last_name', 'email', 'telefono', 'role', 'sede', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
    )
admin.site.register(User)
admin.site.register(Sede)
admin.site.register(Producto)
admin.site.register(Venta)
admin.site.register(DetalleVenta)
admin.site.register(Cliente)
