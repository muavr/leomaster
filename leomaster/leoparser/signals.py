from django.db.models.signals import post_save
from django.dispatch import receiver
from leoparser.models import Document, DocDelta, RemovableHistoryDocument


@receiver(post_save, sender=Document)
def save_document_delta(sender, instance, **kwargs):
    delta = list(instance.delta)
    if delta:
        DocDelta.objects.create(base=instance, delta=delta)


@receiver(post_save, sender=RemovableHistoryDocument)
def save_removable_history_document_delta(sender, instance, **kwargs):
    delta = list(instance.delta)
    if delta:
        DocDelta.objects.create(base=instance, delta=delta)
