from SSP.models import Notification

def notification_context(request):

    if request.user.is_authenticated:

        unread_notif = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()

        notifications = Notification.objects.filter(
            recipient=request.user
        ).order_by("-created_at")[:5]

    else:
        unread_notif = 0
        notifications = []

    return {
        "notifications": notifications,
        "unread_notif": unread_notif,
    }