from django.db import models

from ckeditor.fields import RichTextField
from slugify import slugify

class Patient(models.Model):
    name = models.CharField(max_length=50)
    published = models.BooleanField(default=False)

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

    content = RichTextField(
        null=True
    )

    

