from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django import forms
from django.contrib.auth.models import Group
from .models import User, Rol, Sede, Cliente, Producto, Venta, DetalleVenta

# Formulario personalizado para el modelo User


class UserAdminForm(forms.ModelForm):
    class Meta:
        model = User
        fields = '__all__'

    # Campos para la contraseña (similar al formulario predeterminado del admin)
    password1 = forms.CharField(
        label='Contraseña', widget=forms.PasswordInput, required=False)
    password2 = forms.CharField(
        label='Confirmar contraseña', widget=forms.PasswordInput, required=False)

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        # Validar que las contraseñas coincidan
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        # Si se proporcionó una contraseña, encriptarla
        password = self.cleaned_data.get('password1')
        if password:
            user.set_password(password)
        else:
            # Si no se proporciona una contraseña, asegurarse de que el campo password no se modifique
            if not user.pk:  # Si es un usuario nuevo, establecer una contraseña no utilizable
                user.set_unusable_password()
        if commit:
            user.save()
            # Sincronizar el grupo con el rol, pero solo si role está definido
            if user.role and user.role.rol:
                group_name = user.role.rol.capitalize()  # Ejemplo: 'contable' -> 'Contable'
                group, created = Group.objects.get_or_create(name=group_name)
                # No limpiar los grupos seleccionados manualmente en el formulario
                if not user.groups.exists():  # Solo asignar si no se seleccionó un grupo manualmente
                    user.groups.add(group)
        return user

# Personalizar el admin para el modelo User


class UserAdmin(BaseUserAdmin):
    form = UserAdminForm
    list_display = ('username', 'first_name', 'last_name', 'role',
                    'sede', 'is_staff', 'is_superuser', 'get_groups')
    list_filter = ('role', 'sede', 'is_staff', 'is_superuser')
    search_fields = ('username', 'first_name', 'last_name')
    ordering = ('username',)

    fieldsets = (
        (None, {'fields': ('username',)}),
        ('Información Personal', {'fields': ('first_name', 'last_name', 'email', 'telefono')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Información Adicional', {'fields': ('role', 'sede')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'first_name', 'last_name', 'email', 'telefono', 'role', 'sede', 'is_active', 'is_staff', 'is_superuser', 'groups'),
        }),
    )

    def get_fieldsets(self, request, obj=None):
        if not obj:  # Si es un usuario nuevo
            return self.add_fieldsets
        # Si es un usuario existente, no mostramos los campos de contraseña
        return self.fieldsets

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:  # Si es un usuario existente, deshabilitar el campo username
            form.base_fields['username'].disabled = True
        return form

    def get_groups(self, obj):
        return ", ".join([group.name for group in obj.groups.all()])
    get_groups.short_description = 'Grupos'


# Registrar los modelos en el admin
admin.site.register(User, UserAdmin)
admin.site.register(Rol)
admin.site.register(Sede)
admin.site.register(Cliente)
admin.site.register(Producto)
admin.site.register(Venta)
admin.site.register(DetalleVenta)
