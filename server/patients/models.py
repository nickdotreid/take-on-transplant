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
        blank = True,
        null = True,
        upload_to = 'photos'
    )
    thumbnail = models.ImageField(
        blank = True,
        null = True,
        upload_to = 'thumbnails'
    )

    tags = models.ManyToManyField(
        Tag,
        blank = True
    )

    @property
    def attributes(self):
        if not hasattr(self, '_attributes'):
            self._attributes = self.get_patient_attributes()
        return self._attributes

    @property
    def story_highlights(self):
        if not hasattr(self, '_story_highlights'):
            self._story_highlights = self.get_story_highlights()
        return self._story_highlights

    @property
    def stories(self):
        if not hasattr(self, '_stories'):
            self._stories = self.get_stories()
        return self._stories

    def save(self, *args, **kwargs):
        if self.photo and not self.thumbnail:
            image = Image.open(self.photo)
            image.convert('RGB')
            image.thumbnail((100,100))
            image_io = BytesIO()
            image.save(image_io, 'JPEG', quality=85)
            self.thumbnail = File(
                image_io,
                name = self.photo.name
            )
        super().save(*args, **kwargs)

    def slug(self):
        return slugify(self.name)

    def __str__(self):
        if self.published:
            return '{} (published)'.format(self.name)
        else:
            return '{} (unpublished)'.format(self.name)

    def get_patient_attributes(self):
        return PatientAttribute.objects.filter(
            patient = self
        ).all()

    def get_stories(self):
        return PatientStory.objects.filter(
            patient = self,
            published = True
        ).all()

    def get_story_highlights(self):
        return PatientStoryHighlight.objects.filter(
            patient = self,
            published = True
        ).all()

class Attribute(models.Model):
    name = models.CharField(max_length=250)
    order = models.PositiveIntegerField()
    published = models.BooleanField(default = True)

    def __str__(self):
        return self.name

class PatientAttributeManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset() \
        .prefetch_related('attribute') \
        .order_by('attribute__order') \
        .filter(
            attribute__published = True
        )

class PatientAttribute(models.Model):
    patient = models.ForeignKey(
        Patient,
        on_delete = models.CASCADE,
        related_name = '+'
    )
    attribute = models.ForeignKey(
        Attribute,
        on_delete = models.CASCADE,
        related_name = '+'
    )
    value = models.CharField(max_length=250)

    objects = PatientAttributeManager()

    @property
    def name(self):
        return self.attribute.name

class PatientStory(models.Model):
    patient = models.ForeignKey(
        Patient,
        on_delete = models.CASCADE,
        related_name = '+'
    )

    title = models.CharField(max_length=250)
    published = models.BooleanField(default = True)
    order = models.PositiveIntegerField()

    content = RichTextField(
        blank = True,
        null=True
    )

    tags = models.ManyToManyField(
        Tag,
        blank = True
    )

class PatientStoryHighlight(models.Model):
    patient = models.ForeignKey(
        Patient,
        on_delete = models.CASCADE,
        related_name = '+'
    )

    order = models.PositiveIntegerField()
    published = models.BooleanField(default=True)

    title = models.CharField(
        blank = True,
        max_length = 250,
        null = True
    )
    content = models.CharField(
        blank = True,
        null = True,
        max_length = 500
    )

    tags = models.ManyToManyField(Tag)
