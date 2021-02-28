from django.db import models

from study_sessions.models import StudySession

class HighlightedContent(models.Model):
    session = models.ForeignKey(
        StudySession,
        null = True,
        on_delete = models.CASCADE,
        related_name = '+'
    )
    content_id = models.CharField(
        max_length=100
    )

    content = models.TextField(
        null = True
    )


class Highlight(models.Model):
    session = models.ForeignKey(
        StudySession,
        on_delete = models.CASCADE,
        related_name = '+'
    )

    content = models.ForeignKey(
        HighlightedContent,
        on_delete = models.CASCADE,
        null = True
    )
    text = models.CharField(
        max_length=500,
        null=True
    )
    
    deleted = models.BooleanField(default=False)
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)

