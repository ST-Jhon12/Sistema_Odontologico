from datetime import date

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from django.forms import modelform_factory
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.generic import DeleteView, FormView, ListView

from .forms import LoginForm, RegistrationForm, ReportFilterForm
from .models import (
    Cita,
    Diagnostico,
    Especialidad,
    Odontologo,
    Paciente,
    Receta,
    Tratamiento,
)


RECORDS = {
    'pacientes': {
        'title': 'Pacientes',
        'model': Paciente,
        'fields': ('dni', 'nombres', 'apellidos', 'telefono', 'correo'),
        'search': ('dni', 'nombres', 'apellidos', 'correo'),
    },
    'odontologos': {
        'title': 'Odontólogos',
        'model': Odontologo,
        'fields': ('nombres', 'apellidos', 'numero_colegiatura', 'especialidad', 'estado'),
        'search': ('nombres', 'apellidos', 'numero_colegiatura', 'correo'),
    },
    'especialidades': {
        'title': 'Especialidades',
        'model': Especialidad,
        'fields': ('nombre', 'descripcion', 'estado'),
        'search': ('nombre', 'descripcion'),
    },
    'citas': {
        'title': 'Citas',
        'model': Cita,
        'fields': ('fecha', 'hora', 'paciente', 'odontologo', 'motivo', 'estado'),
        'search': ('paciente__nombres', 'paciente__apellidos', 'motivo'),
    },
    'diagnosticos': {
        'title': 'Diagnósticos',
        'model': Diagnostico,
        'fields': ('fecha', 'cita', 'descripcion'),
        'search': ('cita__paciente__nombres', 'cita__paciente__apellidos', 'descripcion'),
    },
    'tratamientos': {
        'title': 'Tratamientos',
        'model': Tratamiento,
        'fields': ('nombre', 'diagnostico', 'fecha_inicio', 'costo', 'estado'),
        'search': (
            'nombre',
            'diagnostico__cita__paciente__nombres',
            'diagnostico__cita__paciente__apellidos',
        ),
    },
    'recetas': {
        'title': 'Recetas',
        'model': Receta,
        'fields': ('fecha_emision', 'diagnostico', 'medicamento', 'dosis', 'duracion'),
        'search': (
            'medicamento',
            'diagnostico__cita__paciente__nombres',
            'diagnostico__cita__paciente__apellidos',
        ),
    },
}

REPORTS = {
    'citas': {
        'title': 'Citas',
        'model': Cita,
        'date_field': 'fecha',
        'fields': ('fecha', 'hora', 'paciente', 'odontologo', 'motivo', 'estado'),
        'search': ('paciente__nombres', 'paciente__apellidos', 'motivo'),
    },
    'diagnosticos': {
        'title': 'Diagnósticos',
        'model': Diagnostico,
        'date_field': 'fecha',
        'fields': ('fecha', 'cita', 'descripcion', 'recomendaciones'),
        'search': ('cita__paciente__nombres', 'cita__paciente__apellidos', 'descripcion'),
    },
    'tratamientos': {
        'title': 'Tratamientos',
        'model': Tratamiento,
        'date_field': 'fecha_inicio',
        'fields': ('fecha_inicio', 'diagnostico', 'nombre', 'costo', 'estado'),
        'search': (
            'nombre',
            'diagnostico__cita__paciente__nombres',
            'diagnostico__cita__paciente__apellidos',
        ),
    },
    'recetas': {
        'title': 'Recetas',
        'model': Receta,
        'date_field': 'fecha_emision',
        'fields': ('fecha_emision', 'diagnostico', 'medicamento', 'dosis', 'frecuencia'),
        'search': (
            'medicamento',
            'diagnostico__cita__paciente__nombres',
            'diagnostico__cita__paciente__apellidos',
        ),
    },
}


def record_config(slug):
    if slug not in RECORDS:
        from django.http import Http404

        raise Http404('El módulo solicitado no existe.')
    return RECORDS[slug]


def record_form(model):
    def style_field(db_field, **kwargs):
        field = db_field.formfield(**kwargs)
        if field is None:
            return None
        field.widget.attrs['class'] = 'form-control'
        if db_field.get_internal_type() == 'DateField':
            field.widget.input_type = 'date'
        elif db_field.get_internal_type() == 'TimeField':
            field.widget.input_type = 'time'
        return field

    return modelform_factory(
        model,
        fields='__all__',
        formfield_callback=style_field,
    )


class RememberMeLoginView(LoginView):
    template_name = 'control/login.html'
    authentication_form = LoginForm

    def form_valid(self, form):
        response = super().form_valid(form)
        self.request.session.set_expiry(
            60 * 60 * 24 * 30 if form.cleaned_data.get('remember_me') else 0
        )
        return response


def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = RegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, 'Tu cuenta quedó lista. Bienvenido al consultorio.')
        return redirect('dashboard')
    return render(request, 'control/register.html', {'form': form})


@login_required
def dashboard(request):
    today = timezone.localdate()
    context = {
        'patient_count': Paciente.objects.count(),
        'appointment_count': Cita.objects.count(),
        'diagnosis_count': Diagnostico.objects.count(),
        'treatment_count': Tratamiento.objects.count(),
        'today_appointments': Cita.objects.filter(fecha=today)
        .exclude(estado=Cita.Estado.CANCELADA)
        .select_related('paciente', 'odontologo')
        .order_by('hora')[:8],
        'upcoming_count': Cita.objects.filter(
            fecha__gte=today,
            estado__in=(Cita.Estado.PENDIENTE, Cita.Estado.CONFIRMADA),
        ).count(),
    }
    return render(request, 'control/dashboard.html', context)


class RecordListView(LoginRequiredMixin, ListView):
    template_name = 'control/records.html'
    context_object_name = 'records'
    paginate_by = 20

    def dispatch(self, request, *args, **kwargs):
        self.config = record_config(kwargs['slug'])
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        model = self.config['model']
        relations = [
            field
            for field in self.config['fields']
            if model._meta.get_field(field).many_to_one
        ]
        queryset = model.objects.select_related(*relations)
        query = self.request.GET.get('q', '').strip()
        if query:
            search = Q()
            for field in self.config['search']:
                search |= Q(**{f'{field}__icontains': query})
            queryset = queryset.filter(search)
        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.config)
        context['slug'] = self.kwargs['slug']
        context['columns'] = [
            str(self.config['model']._meta.get_field(field).verbose_name).capitalize()
            for field in self.config['fields']
        ]
        context['rows'] = [
            {
                'object': record,
                'cells': [
                    display_value(record, field)
                    for field in self.config['fields']
                ],
            }
            for record in context['records']
        ]
        return context


def display_value(record, field):
    value = getattr(record, field)
    if isinstance(value, date) and not hasattr(value, 'hour'):
        return value.strftime('%d/%m/%Y')
    if hasattr(value, 'hour'):
        return value.strftime('%H:%M')
    if hasattr(record, f'get_{field}_display'):
        return getattr(record, f'get_{field}_display')()
    return value


class RecordFormView(LoginRequiredMixin, FormView):
    template_name = 'control/record_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.config = record_config(kwargs['slug'])
        self.record = None
        self.form_class = record_form(self.config['model'])
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.kwargs.get('pk') is not None:
            self.record = get_object_or_404(
                self.config['model'],
                pk=self.kwargs['pk'],
            )
        kwargs['instance'] = self.record
        return kwargs

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'El registro se guardó correctamente.')
        return redirect('records', slug=self.kwargs['slug'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.config)
        context['slug'] = self.kwargs['slug']
        context['is_edit'] = self.record is not None
        return context


class RecordDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'control/record_confirm_delete.html'

    def dispatch(self, request, *args, **kwargs):
        self.config = record_config(kwargs['slug'])
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return self.config['model'].objects.all()

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            self.object.delete()
        except ProtectedError:
            messages.error(
                request,
                'No se puede eliminar este registro porque otros datos clínicos dependen de él.',
            )
        else:
            messages.success(request, 'El registro se eliminó correctamente.')
        return redirect('records', slug=self.kwargs['slug'])

    def get_success_url(self):
        return reverse('records', kwargs={'slug': self.kwargs['slug']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.config)
        context['slug'] = self.kwargs['slug']
        return context


@login_required
def reports(request):
    return render(
        request,
        'control/reports.html',
        {'report_types': [(slug, config['title']) for slug, config in REPORTS.items()]},
    )


@login_required
def report_detail(request, slug):
    from django.http import Http404

    if slug not in REPORTS:
        raise Http404('El reporte solicitado no existe.')
    config = REPORTS[slug]
    model = config['model']
    relations = [
        field
        for field in config['fields']
        if model._meta.get_field(field).many_to_one
    ]
    queryset = model.objects.select_related(*relations)
    status_choices = (
        config['model']._meta.get_field('estado').choices
        if any(field.name == 'estado' for field in config['model']._meta.fields)
        else ()
    )
    filter_form = ReportFilterForm(
        request.GET or None,
        status_choices=status_choices,
    )
    if filter_form.is_valid():
        start = filter_form.cleaned_data['desde']
        end = filter_form.cleaned_data['hasta']
        status = filter_form.cleaned_data['estado']
        query = filter_form.cleaned_data['q']
        if start:
            queryset = queryset.filter(**{f'{config["date_field"]}__gte': start})
        if end:
            queryset = queryset.filter(**{f'{config["date_field"]}__lte': end})
        if status:
            queryset = queryset.filter(estado=status)
        if query:
            search = Q()
            for field in config['search']:
                search |= Q(**{f'{field}__icontains': query})
            queryset = queryset.filter(search)

    columns = [
        str(config['model']._meta.get_field(field).verbose_name).capitalize()
        for field in config['fields']
    ]
    rows = [
        [display_value(record, field) for field in config['fields']]
        for record in queryset.distinct()[:1000]
    ]
    return render(
        request,
        'control/report_detail.html',
        {
            'slug': slug,
            'title': config['title'],
            'columns': columns,
            'rows': rows,
            'status_choices': status_choices,
            'form': filter_form,
        },
    )
