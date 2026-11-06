from django.db import models

from .diagnostico import Diagnostico


class Receta(models.Model):
    diagnostico = models.ForeignKey(
        Diagnostico,
        on_delete=models.PROTECT,
        related_name='recetas',
        verbose_name='diagnóstico',
    )
    medicamento = models.CharField('medicamento', max_length=150)
    dosis = models.CharField('dosis', max_length=100)
    frecuencia = models.CharField('frecuencia', max_length=100)
    duracion = models.CharField('duración', max_length=100)
    indicaciones = models.TextField('indicaciones', blank=True)
    fecha_emision = models.DateField('fecha de emisión')

    class Meta:
        ordering = ['-fecha_emision']
        verbose_name = 'receta'
        verbose_name_plural = 'recetas'

    def __str__(self):
        return f'{self.medicamento} - {self.diagnostico.cita.paciente}'
