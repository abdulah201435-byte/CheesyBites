"""
WSGI config for CheesyBites project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.1/howto/deployment/wsgi/
"""

import os
import sys

path = '/home/abdullah001/CheesyBites/CheesyBites'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'CheesyBites.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
