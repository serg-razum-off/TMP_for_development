from .models import UserMessage

def message_context(request):
    if request.user.is_authenticated:
        return {
            'unread_messages_count': UserMessage.objects.filter(user=request.user, is_read=False, is_deleted=False).count()
        }
    return {'unread_messages_count': 0}
