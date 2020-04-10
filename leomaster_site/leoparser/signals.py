from django.db.models.signals import post_save
from django.dispatch import receiver
from leoparser.models import Document, DocDelta


@receiver(post_save, sender=Document)
def save_document_delta(sender, instance, **kwargs):
    delta = list(instance.delta)
    if delta:
        DocDelta.objects.create(base=instance, delta=delta)
