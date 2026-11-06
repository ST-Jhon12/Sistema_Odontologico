from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError
from django.db import models
from django.apps import apps
from django.test import RequestFactory, SimpleTestCase

from .forms import ReportFilterForm
from .models import (
    Cita,
    Diagnostico,
    Especialidad,
    Odontologo,
    Paciente,
    Receta,
    Tratamiento,
)
from .views import RecordFormView, RecordListView, record_form


class BusinessModelTests(SimpleTestCase):
    def test_exactly_seven_business_models_are_registered(self):
        self.assertEqual(
            {model.__name__ for model in apps.get_app_config('control').get_models()},
            {
                'Paciente',
                'Odontologo',
                'Especialidad',
                'Cita',
                'Diagnostico',
                'Tratamiento',
                'Receta',
            },
        )

    def test_clinical_relationships_protect_referenced_records(self):
        foreign_keys = (
            (Odontologo, 'especialidad'),
            (Cita, 'paciente'),
            (Cita, 'odontologo'),
            (Diagnostico, 'cita'),
            (Tratamiento, 'diagnostico'),
            (Receta, 'diagnostico'),
        )
        for model, field_name in foreign_keys:
            with self.subTest(model=model.__name__, field=field_name):
                self.assertIs(
                    model._meta.get_field(field_name).remote_field.on_delete,
                    models.PROTECT,
                )

    def test_patient_dni_requires_eight_digits(self):
        dni = Paciente._meta.get_field('dni')
        dni.run_validators('12345678')
        with self.assertRaises(ValidationError):
            dni.run_validators('1234567')

    def test_crud_forms_use_native_date_and_time_inputs(self):
        self.assertEqual(
            record_form(Paciente).base_fields['fecha_nacimiento'].widget.input_type,
            'date',
        )
        self.assertEqual(
            record_form(Cita).base_fields['hora'].widget.input_type,
            'time',
        )


class ReportFilterTests(SimpleTestCase):
    def test_report_filter_accepts_date_range_and_status_options(self):
        form = ReportFilterForm(
            {'desde': '2026-01-01', 'hasta': '2026-01-31', 'estado': 'Pendiente'},
            status_choices=(('Pendiente', 'Pendiente'),),
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_report_filter_rejects_reversed_dates(self):
        form = ReportFilterForm({'desde': '2026-02-01', 'hasta': '2026-01-31'})
        self.assertFalse(form.is_valid())
        self.assertIn('hasta', form.errors)


class AccessControlTests(SimpleTestCase):
    def test_anonymous_users_are_redirected_from_patient_records(self):
        request = RequestFactory().get('/pacientes/')
        request.user = AnonymousUser()
        response = RecordListView.as_view()(request, slug='pacientes')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/cuenta/ingresar/', response['Location'])

    def test_anonymous_users_cannot_probe_record_ids(self):
        request = RequestFactory().get('/pacientes/999999/editar/')
        request.user = AnonymousUser()
        response = RecordFormView.as_view()(
            request,
            slug='pacientes',
            pk=999999,
        )
        self.assertEqual(response.status_code, 302)
