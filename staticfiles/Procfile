web: gunicorn socialapp.wsgi --log-file -

web: python manage.py migrate && gunicorn socialapp.wsgi