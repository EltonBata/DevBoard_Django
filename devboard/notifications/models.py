from django.db import models
from tasks.models import Task


# Create your models here.
class Notification(models.Model):

    TYPE_CHOICE = [
        ("assigned", "Assigned"),
        ("comment", "Comment"),
        ("status_change", "Status Change"),
    ]

    user = models.ForeignKey(
        "auth.User", on_delete=models.CASCADE, related_name="notifications"
    )
    type = models.CharField(max_length=20, choices=TYPE_CHOICE)
    text_message = models.TextField()
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, related_name="notifications"
    )
    was_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.type} notification for {self.user}"

    class Meta:
        ordering = ["-created_at"]

