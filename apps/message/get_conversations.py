from apps.message.lib.clock import Clock
from .models import Conversation


def get_conversation(sender, receiver):
    conversation_instances = Conversation.objects.filter(sender=sender, receiver=receiver)
    if conversation_instances.exists():
        conversation_instance = conversation_instances.last()
        conversation_instance.last_updated_on =Clock.utc_now()
        conversation_instance.save()
    else:
        conversation_instance = Conversation()
        conversation_instance.sender = sender
        conversation_instance.receiver = receiver
        conversation_instance.save()
    return conversation_instance
