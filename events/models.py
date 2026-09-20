

# Create your models here.
from django.db import models
from django.contrib.auth.models import User


class Event(models.Model):

    STATUS_CHOICES = [
        ("Upcoming", "Upcoming"),
        ("Ongoing", "Ongoing"),
        ("Completed", "Completed"),
        ("Cancelled", "Cancelled"),
    ]

    name = models.CharField(max_length=200)

    description = models.TextField()

    date = models.DateTimeField()

    venue = models.CharField(max_length=200)

    capacity = models.PositiveIntegerField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Upcoming"
    )

    def __str__(self):
        return self.name


class EventRegistration(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE
    )

    registered_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        unique_together = ("user", "event")

    def __str__(self):
        return f"{self.user.username} - {self.event.name}"