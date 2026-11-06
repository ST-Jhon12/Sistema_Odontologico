# Sonrisa Perfecta

Sistema web Django para gestionar pacientes, odontólogos, especialidades, citas, diagnósticos, tratamientos y recetas.

## Configuración

1. Instala las dependencias con `pip install -r requirements.txt`.
2. Crea la base MySQL `consultorio_odontologico` o configura `DB_NAME`.
3. Configura opcionalmente las variables `DB_USER`, `DB_PASSWORD`, `DB_HOST` y `DB_PORT`. Los valores predeterminados son `root`, contraseña vacía, `localhost` y `3306`.
4. Ejecuta las migraciones y crea una cuenta de acceso:

   ```powershell
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py runserver
   ```

5. Abre `http://127.0.0.1:8000/`. También es posible registrar una cuenta desde la pantalla de inicio de sesión.

Para producción, configura `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=False` y `DJANGO_ALLOWED_HOSTS` mediante variables de entorno. Los reportes se filtran en la página y se pueden imprimir o guardar en PDF desde el diálogo de impresión del navegador.
