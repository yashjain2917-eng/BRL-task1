from django.urls import path

from .views import (
    events,
    event_detail,
    register_user,
    login_user,
    current_user,
    logout_user,
    register_event,
)

urlpatterns = [

    # Authentication
    path("auth/register/", register_user),
    path("auth/login/", login_user),
    path("auth/me/", current_user),
    path("auth/logout/", logout_user),

    # Event CRUD
    path("events/", events),
    path("events/<int:event_id>/", event_detail),

    # Event Registration
    path(
        "events/<int:event_id>/register/",
        register_event
    ),
]