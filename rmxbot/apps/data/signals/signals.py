
import django.dispatch


get_data = django.dispatch.Signal(providing_args=["docids"])

create_data = django.dispatch.Signal(providing_args=["docid", "corpus_id"])
