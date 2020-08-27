import django.dispatch


# Arguments: "instance",  "history_instance", "history_date",
#            "history_user", "history_change_reason", "using"
pre_create_historical_record = django.dispatch.Signal()

# Arguments: "instance",  "history_instance", "history_date",
#            "history_user", "history_change_reason", "using"
post_create_historical_record = django.dispatch.Signal()
