import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'djwed.settings'

sys.path.append('/var/www/wedding')

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()


