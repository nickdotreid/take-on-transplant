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

class Article(models.Model):
    title = models.CharField(max_length=500)
    published = models.BooleanField(default=True)
    order = models.PositiveIntegerField(
        blank = True
    )
    parent = models.ForeignKey(
        'self',
        blank = True,
        null = True,
        on_delete = models.CASCADE,
        related_name = '+'
    )

    
    description = models.CharField(
        blank = True,
        null = True,
        max_length = 500
    )
    content = RichTextField(
        null = True
    )

    def save(self, *args, **kwargs):
        if not self.order:
            self.order = (Article.objects.count() + 1) * 10
        super().save(*args, **kwargs)

    def __str__(self):
        return '{title} ({status})'.format(
            title = self.title,
            status = 'published' if self.published else 'unpublished'
        )
