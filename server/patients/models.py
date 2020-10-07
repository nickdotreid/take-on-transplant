from io import BytesIO
from django.core.files import File
from django.db import models
from PIL import Image

from ckeditor.fields import RichTextField
from slugify import slugify

from tags.models import Tag

class Patient(models.Model):
    name = models.CharField(max_length=50)
    published = models.BooleanField(default=False)
    photo = models.ImageField(
        null = True,
        upload_to = 'photos'
    )
    thumbnail = models.ImageField(
        null = True,
        upload_to = 'thumbnails'
    )

    tags = models.ManyToManyField(Tag)

    def save(self, *args, **kwargs):
        if self.photo:
            image = Image.open(self.photo)
            image.convert('RGB')
            image.thumbnail((100,100))
            image_io = BytesIO()
            image.save(image_io, 'JPEG', quality=85)
            self.thumbnail = File(
                image_io,
                name = self.photo.name
            )
        else:
            self.thumbnail = None
        super().save(*args, **kwargs)

    def slug(self):
        return slugify(self.name)

    def __str__(self):
        if self.published:
            return '{} (published)'.format(self.name)
        else:
            return '{} (unpublished)'.format(self.name)

class Property(models.Model):
    name = models.CharField(max_length=250)

    def __str__(self):
        return self.name


class PatientProperty(models.Model):
    patient = models.ForeignKey(
        Patient,
        on_delete = models.CASCADE,
        related_name = '+'
    )
    property = models.ForeignKey(
        Property,
        on_delete = models.CASCADE,
        related_name = '+'
    )
    order = models.PositiveIntegerField()
    published = models.BooleanField(default=True)
    value = models.CharField(max_length=250)

class PatientStory(models.Model):
    patient = models.ForeignKey(
        Patient,
        on_delete = models.CASCADE,
        related_name = '+'
    )

    title = models.CharField(max_length=250)
    published = models.BooleanField(default = True)
    order = models.PositiveIntegerField()

    excerpt = models.CharField(
        null = True,
        max_length = 500
    )

    content = RichTextField(
        null=True
    )

    tags = models.ManyToManyField(Tag)
