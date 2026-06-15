from django.shortcuts import render, get_object_or_404, redirect
from .models import Task, Project, Tag, Comment
from django.db.models import Avg, Max, Min, Count, Q


def dashboard(request):

    task_stats = Task.objects.aggregate(
        total=Count("id"),
        total_todo=Count("id", filter=Q(status="todo")),
        total_in_progress=Count("id", filter=Q(status="in_progress")),
        total_done=Count("id", filter=Q(status="done")),
        priority_avg=Avg("priority"),
    )

    biggest_project = (
        Project.objects.annotate(total=Count("tasks")).order_by("-total").first()
    )

    context = {
        "total_tasks": task_stats["total"],
        "total_todo": task_stats["total_todo"],
        "total_in_progress": task_stats["total_in_progress"],
        "total_done": task_stats["total_done"],
        "priority_avg": task_stats["priority_avg"],
        "biggest_project": biggest_project,
    }

    return render(request, "dashboard.html", context)


def task_list(request):
    status_filter = request.GET.get("status")
    priority_filter = request.GET.get("priority")
    project_filter = request.GET.get("project")

    tasks = Task.objects.all()

    if status_filter:
        tasks = tasks.filter(status=status_filter)
    if priority_filter:
        tasks = tasks.filter(priority=priority_filter)
    if project_filter:
        tasks = tasks.filter(project__id=project_filter)

    return render(request, "task_list.html", {"task_list": tasks})


def task_detail(request, id):
    task = get_object_or_404(Task, pk=id)

    return render(request, "task_detail.html", {"task": task})


def task_create(request):
    if request.method == "POST":

        project = get_object_or_404(Project, pk=request.POST["project_id"])

        task = Task()
        task.title = request.POST["title"]
        task.description = request.POST["description"]
        task.priority = request.POST["priority"]
        task.project = project

        task.save()

        tags_id = request.POST.getlist("tags_id")
        task.tags.add(Tag.objects.filter(pk__in=tags_id))

        return redirect("tasks:detail", id=task.pk)


def task_update(request, id):
    if request.method == "POST":

        task = get_object_or_404(Task, pk=id)

        project = get_object_or_404(Project, pk=request.POST["project_id"])

        task.title = request.POST["title"]
        task.description = request.POST["description"]
        task.priority = request.POST["priority"]
        task.project = project

        task.save()

        tags_id = request.POST.getlist("tags_id")
        task.tags.set(Tag.objects.filter(pk__in=tags_id))

        return redirect("tasks:detail", id=task.pk)


@login_required
def task_comment(request, task_id):

    if request.method == "POST":
        task = get_object_or_404(Task, pk=task_id)

        Comment.objects.create(
            task=task, author=request.user, body=request.POST["body"]
        )

        return redirect("tasks:detail", id=task_id)
    return redirect("tasks:list")


def task_delete(request, id):
    if request.method == "POST":

        task = get_object_or_404(Task, pk=id)

        task.delete()

        return redirect("tasks:list")


def project_list(request):
    projects = Project.objects.annotate(
        total_tasks=Count("tasks"),
        total_tasks_done=Count("tasks__id", filter=Q(tasks__status="done")),
    )

    search = request.GET.get("search")

    if search:
        projects = projects.filter(
            Q(name__icontains=search) | Q(description__icontains=search)
        )

    return render(request, "projects/project_list.html", {"projects": projects})


def project_detail(request, id):

    project = get_object_or_404(Project, pk=id)

    tasks = project.tasks.all()
    total_tasks = tasks.count()
    total_todo = tasks.filter(status="todo").count()
    total_in_progress = tasks.filter(status="in_progress").count()
    total_done = tasks.filter(status="done").count()

    done_percent = (total_done / total_tasks * 100) if total_todo > 0 else 0

    context = {
        "project": project,
        "tasks": tasks,
        "total_tasks": total_tasks,
        "total_todo": total_todo,
        "total_in_progress": total_in_progress,
        "total_done": total_done,
        "done_percent": done_percent,
    }

    return render(request, "project/project_detail.html", context)


@login_required
def user_stats(request):

    user = request.user

    tasks_stats = Task.objects.filter(assigned_to=user).aggregate(
        total_todo=Count("id", filter=Q(status="todo")),
        in_progress=Count("id", filter=Q(status="in_progress")),
        total_done=Count("id", filter=Q(status="todo")),
    )

    total_comments = Comment.objects.filter(author=user).count()

    biggest_project = (
        Project.objects.filter(tasks__assigned_to=user)
        .annotate(total_tasks=Count("tasks"))
        .order_by("-total_tasks")
        .first()
    )

    context = {
        **tasks_stats,
        "total_comments": total_comments,
        "biggest_project": biggest_project,
    }
