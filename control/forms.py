from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User


class ReportFilterForm(forms.Form):
    desde = forms.DateField(
        label='Desde',
        required=False,
        input_formats=['%Y-%m-%d'],
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
    )
    hasta = forms.DateField(
        label='Hasta',
        required=False,
        input_formats=['%Y-%m-%d'],
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
    )
    q = forms.CharField(
        label='Buscar paciente o detalle',
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'type': 'search',
                'placeholder': 'Nombre o descripción',
            }
        ),
    )
    estado = forms.ChoiceField(
        label='Estado',
        required=False,
        choices=(('', 'Todos'),),
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    def __init__(self, *args, status_choices=(), **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['estado'].choices = (('', 'Todos'), *status_choices)

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('desde')
        end = cleaned_data.get('hasta')
        if start and end and start > end:
            self.add_error('hasta', 'La fecha final debe ser igual o posterior a la inicial.')
        return cleaned_data


class LoginForm(AuthenticationForm):
    remember_me = forms.BooleanField(
        label='Mantener mi cuenta abierta',
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update(
            {'class': 'form-control', 'autocomplete': 'username'}
        )
        self.fields['password'].widget.attrs.update(
            {'class': 'form-control', 'autocomplete': 'current-password'}
        )


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(label='Correo electrónico')
    first_name = forms.CharField(label='Nombres', max_length=150)
    last_name = forms.CharField(label='Apellidos', max_length=150)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
