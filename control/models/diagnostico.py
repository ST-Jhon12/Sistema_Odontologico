from django.db import models

from .cita import Cita


class Diagnostico(models.Model):
    cita = models.ForeignKey(
        Cita,
        on_delete=models.PROTECT,
        related_name='diagnosticos',
        verbose_name='cita',
    )
    descripcion = models.TextField('descripción')
    recomendaciones = models.TextField('recomendaciones', blank=True)
    fecha = models.DateField('fecha')

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'diagnóstico'
        verbose_name_plural = 'diagnósticos'

    def __str__(self):
        return f'Diagnóstico de {self.cita.paciente} ({self.fecha:%d/%m/%Y})'
