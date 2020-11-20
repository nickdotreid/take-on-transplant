from django.db import models
from ckeditor.fields import RichTextField
from slugify import slugify

class AbstractResource(models.Model):
    name = models.CharField(max_length = 140)
    slug = models.CharField(null=True, max_length=160)
    published = models.BooleanField(default=True)
    description = models.CharField(
        null = True,
        max_length = 500
    )

    class Meta:
        abstract = True
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug and self.name:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        status = 'unpublished'
        if self.published:
            status = 'published'
        return '{} ({})'.format(self.name, status)

class Definition(AbstractResource):
    pass

class Resource(AbstractResource):
    content = RichTextField(
        null = True
    )
