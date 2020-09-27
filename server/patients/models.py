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

    

