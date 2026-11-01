import os
import sys

# Path to the directory containing manage.py
path = '/home/abdullah001/CheesyBites/CheesyBites'
if path not in sys.path:
    sys.path.append(path)

# Point to your Django settings file
os.environ['DJANGO_SETTINGS_MODULE'] = 'CheesyBites.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
