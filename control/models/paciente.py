from django.core.validators import RegexValidator
from django.db import models


class Paciente(models.Model):
    nombres = models.CharField('nombres', max_length=100)
    apellidos = models.CharField('apellidos', max_length=100)
    dni = models.CharField(
        'DNI',
        max_length=8,
        unique=True,
        validators=[RegexValidator(r'^\d{8}$', 'El DNI debe tener 8 dígitos.')],
    )
    fecha_nacimiento = models.DateField('fecha de nacimiento')
    telefono = models.CharField('teléfono', max_length=20)
    direccion = models.CharField('dirección', max_length=200)
    correo = models.EmailField('correo electrónico')
    created_at = models.DateTimeField('fecha de registro', auto_now_add=True)

    class Meta:
        ordering = ['apellidos', 'nombres']
        verbose_name = 'paciente'
        verbose_name_plural = 'pacientes'

    def __str__(self):
        return f'{self.nombres} {self.apellidos}'
