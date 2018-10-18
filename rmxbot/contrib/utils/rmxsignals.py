""" signals used by the apps for inter-app communication """

import django.dispatch


get_data = django.dispatch.Signal(providing_args=['docids'])









