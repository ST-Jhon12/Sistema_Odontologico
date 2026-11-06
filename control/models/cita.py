from django.db import models

from .odontologo import Odontologo
from .paciente import Paciente


class Cita(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = 'Pendiente', 'Pendiente'
        CONFIRMADA = 'Confirmada', 'Confirmada'
        ATENDIDA = 'Atendida', 'Atendida'
        CANCELADA = 'Cancelada', 'Cancelada'

    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.PROTECT,
        related_name='citas',
        verbose_name='paciente',
    )
    odontologo = models.ForeignKey(
        Odontologo,
        on_delete=models.PROTECT,
        related_name='citas',
        verbose_name='odontólogo',
    )
    fecha = models.DateField('fecha')
    hora = models.TimeField('hora')
    motivo = models.CharField('motivo', max_length=200)
    estado = models.CharField(
        'estado', max_length=20, choices=Estado.choices, default=Estado.PENDIENTE
    )
    observaciones = models.TextField('observaciones', blank=True)

    class Meta:
        ordering = ['-fecha', '-hora']
        verbose_name = 'cita'
        verbose_name_plural = 'citas'

    def __str__(self):
        return f'{self.fecha:%d/%m/%Y} - {self.paciente}'
