from django.contrib import admin
from .models import (
    Cita,
    Diagnostico,
    Especialidad,
    Odontologo,
    Paciente,
    Receta,
    Tratamiento,
)


admin.site.register(
    (Paciente, Odontologo, Especialidad, Cita, Diagnostico, Tratamiento, Receta)
)
