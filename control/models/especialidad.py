from django.db import models


class Especialidad(models.Model):
    class Estado(models.TextChoices):
        ACTIVA = 'Activa', 'Activa'
        INACTIVA = 'Inactiva', 'Inactiva'

    nombre = models.CharField('nombre', max_length=100, unique=True)
    descripcion = models.TextField('descripción', blank=True)
    estado = models.CharField(
        'estado', max_length=20, choices=Estado.choices, default=Estado.ACTIVA
    )

    class Meta:
        ordering = ['nombre']
        verbose_name = 'especialidad'
        verbose_name_plural = 'especialidades'

    def __str__(self):
        return self.nombre
