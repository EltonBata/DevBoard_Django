from django.db import models

# Create your models here.


class Project(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    members = models.ManyToManyField("auth.User", related_name='projects')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["created_at"]


class Tag(models.Model):
    name = models.CharField(max_length=20, unique=True)
    color = models.CharField(max_length=20, default="#FF5733")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class Task(models.Model):

    TASK_STATUS = [("todo", "To Do"), ("in_progress", "In Progress"), ("done", "Done")]
    TASK_PRIORITY = [(1, "Low"), (2, "Medium"), (3, "High")]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    assigned_to = models.ForeignKey("auth.User", on_delete=models.SET_NULL, null=True, related_name='assigned_tasks')
    tags = models.ManyToManyField(Tag, blank=True, related_name='tasks')
    status = models.CharField(max_length=20, choices=TASK_STATUS, default='todo')
    priority = models.IntegerField(choices=TASK_PRIORITY, default=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["created_at"]


class Comment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey("auth.User", on_delete=models.CASCADE, related_name='comments')
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author} on '{self.task}'"

    class Meta:
        ordering = ["-created_at"]
