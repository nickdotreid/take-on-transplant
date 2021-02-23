from slugify import slugify

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

class TagCategory(models.Model):
    name = models.CharField(max_length=150)
    order = models.PositiveIntegerField()
    published = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']

    @property
    def slug(self):
        return slugify(self.name)

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length = 150)
    order = models.PositiveIntegerField(
        blank = True,
        null = True
    )
    published = models.BooleanField(default=True)
    
    category = models.ForeignKey(
        TagCategory,
        blank = True,
        null = True,
        on_delete = models.SET_NULL,
        related_name = '+'
    )

    class Meta:
        ordering = ['category', 'order', 'name']

    @property
    def slug(self):
        return slugify(self.name)

    def save(self, *args, **kwargs):
        if not self.order:
            self.order = (Tag.objects.filter(category=self.category).count() + 1) * 10
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class TaggedContent(models.Model):
    tag = models.ForeignKey(Tag,
        on_delete = models.CASCADE,
        related_name='+'
    )

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
