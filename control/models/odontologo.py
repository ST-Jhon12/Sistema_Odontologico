from django.db import models

from .especialidad import Especialidad


class Odontologo(models.Model):
    class Estado(models.TextChoices):
        ACTIVO = 'Activo', 'Activo'
        INACTIVO = 'Inactivo', 'Inactivo'

    nombres = models.CharField('nombres', max_length=100)
    apellidos = models.CharField('apellidos', max_length=100)
    numero_colegiatura = models.CharField(
        'número de colegiatura', max_length=30, unique=True
    )
    telefono = models.CharField('teléfono', max_length=20)
    correo = models.EmailField('correo electrónico')
    especialidad = models.ForeignKey(
        Especialidad,
        on_delete=models.PROTECT,
        related_name='odontologos',
        verbose_name='especialidad',
    )
    estado = models.CharField(
        'estado', max_length=20, choices=Estado.choices, default=Estado.ACTIVO
    )

    class Meta:
        ordering = ['apellidos', 'nombres']
        verbose_name = 'odontólogo'
        verbose_name_plural = 'odontólogos'

    def __str__(self):
        return f'Dr. {self.nombres} {self.apellidos}'
