from django.db import models

from ckeditor.fields import RichTextField

from patients.models import AbstractOrderable
from patients.models import Patient

class FrequentlyAskedQuestion(models.Model):
    text = models.CharField(max_length=500)
    published = models.BooleanField(default=True)

    @property
    def responses(self):
        if not hasattr(self, '_responses'):
            self._responses = self.get_responses()
        return self._responses

    @property
    def number_of_responses(self):
        return len(self.responses)

    def get_responses(self):
        return Answer.objects \
        .filter(
            question = self,
            published = True
        ) \
        .order_by('order') \
        .all()

    def __str__(self):
        return self.text

class Answer(models.Model):
    patient = models.ForeignKey(
        Patient,
        blank = True,
        null = True,
        on_delete = models.CASCADE,
        related_name = '+'
    )
    question = models.ForeignKey(
        FrequentlyAskedQuestion,
        on_delete = models.CASCADE,
        related_name = '+'
    )
    text = RichTextField(
        blank = True,
        null = True
    )

    order = models.PositiveIntegerField()
    published = models.BooleanField(default=True)

    def __str__(self):
        return self.text

class Category(AbstractOrderable):
    
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.order:
            self.order = (Category.objects.count()) + 1 * 10
        super().save(*args, **kwargs)

    @property
    def questions(self):
        questionCategories = QuestionInCategory.objects \
        .filter(
            category = self
        ) \
        .order_by('order') \
        .all()
        return [qc.question for qc in questionCategories]

class QuestionInCategory(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete = models.CASCADE,
        related_name = '+'
    )
    question = models.ForeignKey(
        FrequentlyAskedQuestion,
        on_delete = models.CASCADE,
        related_name = '+'
    )
    order = models.PositiveIntegerField()
