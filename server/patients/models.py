from django.db import models

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

