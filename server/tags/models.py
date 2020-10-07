from django.db import models

class Tag(models.Model):
    name = models.CharField(max_length = 150)
    published = models.BooleanField(default=True)
    warning = models.BooleanField(default=False)

    def __str__(self):
        return self.name
