import random

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

class RelatedItemsList(models.Model):
    name = models.CharField(max_length=500)

    @property
    def items(self):
        return RelatedItem.objects.filter(
            item_list = self
        ) \
        .order_by('order') \
        .all()

    @property
    def content_list(self):
        return [item.content_object for item in RelatedItem.objects.order_by('order').filter(item_list = self).all()]

class RelatedItem(models.Model):
    item_list = models.ForeignKey(
        RelatedItemsList,
        on_delete = models.CASCADE,
        related_name = '+'
    )
    order = models.PositiveIntegerField()

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def save(self, *args, **kwargs):
        if not self.order:
            self.order = (RelatedItem.objects.filter(item_list=self.item_list).count() + 1) * 10
        super().save(*args, **kwargs)
