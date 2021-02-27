from django.db import models

class StudySession(models.Model):

    persona = models.CharField(
        max_length=150,
        null=True
    )
    
    high_agency_version = models.BooleanField()
    integrated_content_version = models.BooleanField()

    start = models.DateTimeField(
        auto_now_add=True
    )
