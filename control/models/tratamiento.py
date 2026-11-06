from django.core.validators import MinValueValidator
from django.db import models

from .diagnostico import Diagnostico


class Tratamiento(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = 'Pendiente', 'Pendiente'
        EN_PROCESO = 'En proceso', 'En proceso'
        FINALIZADO = 'Finalizado', 'Finalizado'

    diagnostico = models.ForeignKey(
        Diagnostico,
        on_delete=models.PROTECT,
        related_name='tratamientos',
        verbose_name='diagnóstico',
    )
    nombre = models.CharField('nombre', max_length=150)
    descripcion = models.TextField('descripción')
    fecha_inicio = models.DateField('fecha de inicio')
    fecha_fin = models.DateField('fecha de finalización', null=True, blank=True)
    costo = models.DecimalField(
        'costo',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    estado = models.CharField(
        'estado', max_length=20, choices=Estado.choices, default=Estado.PENDIENTE
    )

    class Meta:
        ordering = ['-fecha_inicio']
        verbose_name = 'tratamiento'
        verbose_name_plural = 'tratamientos'

    def __str__(self):
        return self.nombre
