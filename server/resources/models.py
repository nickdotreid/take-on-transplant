from django.db import models
from ckeditor.fields import RichTextField
from slugify import slugify

class Resource(models.Model):
    name = models.CharField(max_length = 70)
    slug = models.CharField(null=True, max_length=70)
    published = models.BooleanField(default=True)
    description = models.CharField(
        null = True,
        max_length = 250
    )
    content = RichTextField(
        null = True
    )

    class Meta:
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
