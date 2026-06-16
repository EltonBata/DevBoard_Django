from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Notification
from django.core.exceptions import PermissionDenied


@login_required
def notification_list(request):
    user = request.user
    notifications = Notification.objects.filter(user=user)

    return render(request, "notification_list.html", {"notifications": notifications})


@login_required
def notification_mark_read(request, id):

    if request.method == "POST":
        user = request.user

        notification = get_object_or_404(Notification, pk=id)

        if notification.user != user:
            raise PermissionDenied()

        notification.was_read = True
        notification.save()

    return redirect("notifications:list")


@login_required
def notification_mark_all_read(request):

    if request.method == "POST":
        user = request.user

        Notification.objects.filter(user=user, was_read=False).update(was_read=True)

    return redirect("notifications:list")
