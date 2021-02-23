from io import BytesIO
from django.core.files import File
from django.db import models
from PIL import Image
from PIL import ImageOps
import re

from ckeditor.fields import RichTextField
from slugify import slugify

from resources.models import Resource
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

    @property
    def published_tags(self):
        return self.tags.filter(
            published = True
        ).all()

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

    @property
    def pre_transplant_issues(self):
        if not hasattr(self, '_pre_transplant_issues'):
            self._pre_transplant_issues = self.get_pre_transplant_issues()
        return self._pre_transplant_issues

    @property
    def post_transplant_issues(self):
        if not hasattr(self, '_post_transplant_issues'):
            self._post_transplant_issues = self.get_post_transplant_issues()
        return self._post_transplant_issues

    def save(self, *args, **kwargs):
        self.update_thumbnail()
        super().save(*args, **kwargs)

    def update_thumbnail(self):
        if self.photo:
            image = Image.open(self.photo)
            thumb = ImageOps.fit(image, (200,200), Image.ANTIALIAS)
            image_io = BytesIO()
            thumb.save(image_io, 'JPEG', quality=85)
            self.thumbnail = File(
                image_io,
                name = self.photo.name
            )
        else:
            self.thumbnail = None     

    def slug(self):
        return slugify(self.name)

    def __str__(self):
        if self.published:
            return '{} (published)'.format(self.name)
        else:
            return '{} (unpublished)'.format(self.name)

    def get_patient_attributes(self):
        return PatientAttribute.objects.filter(
            patient = self,
            attribute__published = True
        ).all()

    def get_all_patient_attributes(self):
        return PatientAttribute.objects.filter(
            models.Q(attribute__published=True) | models.Q(attribute__published=False),
            patient = self
        ).all()

    def get_attribute(self, key):
        if not hasattr(self, '_all_attribute_values'):
            self._all_attribute_values = self.get_all_patient_attributes()
        for attribute in self._all_attribute_values:
            if attribute.key == slugify(key):
                return attribute.value
        return None

    def get_attribute_as_int(self, key):
        value = self.get_attribute(key)
        if value is None:
            return value
        else:
            return int(re.sub('\D','',value))

    def get_value(self, keys):
        for key in keys:
            value = self.get_attribute_as_int(key)
            if value is not None:
                return value
        return None
    
    def get_value_pairs(self, keys):
        for key in keys:
            value = self.get_attribute(key)
            if value is not None:
                return value, slugify(value)
        return None, None

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

    def get_pre_transplant_issues(self):
        patient_issues = PretransplantIssue.objects.filter(
            patient = self,
            issue__published = True
        ) \
        .prefetch_related('issue') \
        .order_by('issue__order') \
        .all()
        return [pi.issue for pi in patient_issues]

    def get_post_transplant_issues(self):
        patient_issues = PostTransplantIssue.objects.filter(
            patient = self,
            issue__published = True
        ) \
        .prefetch_related('issue') \
        .order_by('issue__order') \
        .all()
        return [pi.issue for pi in patient_issues]

class AbstractOrderable(models.Model):
    name = models.CharField(max_length=250, null=True)
    order = models.PositiveIntegerField()
    published = models.BooleanField(default = True)

    class Meta:
        abstract = True
        ordering = ['order']

class Attribute(AbstractOrderable):
    name = models.CharField(max_length=250)
    order = models.PositiveIntegerField()
    published = models.BooleanField(default = True)

    resource = models.ForeignKey(
        Resource,
        blank = True,
        on_delete = models.SET_NULL,
        null = True,
        related_name = '+'
    )

    def save(self, *args, **kwargs):
        if not self.order:
            self.order = (Issue.objects.count() + 1) * 10
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class PatientAttributeManager(models.Manager):

    def get_queryset(self):
        queryset = super().get_queryset() \
        .prefetch_related('attribute') \
        .prefetch_related('attribute__resource') \
        .order_by('attribute__order')
        return queryset

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

    @property
    def key(self):
        return slugify(self.attribute.name)

    @property
    def description(self):
        if self.attribute.resource:
            return self.attribute.resource.description
        else:
            return None

class PatientStory(AbstractOrderable):
    patient = models.ForeignKey(
        Patient,
        on_delete = models.CASCADE,
        related_name = '+'
    )

    title = models.CharField(max_length=250)
    content = RichTextField(
        blank = True,
        null=True
    )
    tags = models.ManyToManyField(
        Tag,
        blank = True
    )

class PatientStoryHighlight(AbstractOrderable):
    patient = models.ForeignKey(
        Patient,
        on_delete = models.CASCADE,
        related_name = '+'
    )

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

class Issue(AbstractOrderable):
    name = models.CharField(max_length=250)
    order = models.PositiveIntegerField()
    published = models.BooleanField(default = True)

    def save(self, *args, **kwargs):
        if not self.order:
            self.order = (Issue.objects.count() + 1) * 10
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class AbstractPatientIssue(models.Model):
    patient = models.ForeignKey(
        Patient,
        on_delete = models.CASCADE,
        related_name = '+'
    )
    issue = models.ForeignKey(
        Issue,
        on_delete = models.CASCADE,
        related_name = '+'
    )

    class Meta:
        abstract = True
    
class PretransplantIssue(AbstractPatientIssue):
    pass

class PostTransplantIssue(AbstractPatientIssue):
    pass
