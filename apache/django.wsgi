import os, sys

path = '/home/gda/django'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'vasa.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
