import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'djwed.settings'

local_path = '/var/www/wedding'
# this file is reloaded by apache on changes, so avoid adding the same
# directory over and over to sys.path
if local_path not in sys.path:
  sys.path.append(local_path)

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()


