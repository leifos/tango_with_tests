from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
import os

class Category(models.Model):
    name = models.CharField(max_length=128, unique=True)
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.name

class Page(models.Model):
    category = models.ForeignKey(Category)
    title = models.CharField(max_length=128)
    url = models.URLField()
    views = models.IntegerField(default=0)

    def __unicode__(self):
        return self.title

def file_rename(instance, filename):
        name, extension = os.path.splitext(filename)
        upload_path = 'profile_images'
        filename = "%s_%s%s" % (instance.user.pk, instance.user.username, extension)
        return os.path.join(upload_path, filename)

class UserProfile(models.Model):
    # Change name of the uploaded file

    # This line is required. Links UserProfile to a User model instance.
    user = models.OneToOneField(User)

    # The additional attributes we wish to include.
    website = models.URLField(blank=True)
    picture = models.ImageField(upload_to=file_rename, blank=True,default='profile_images/default.png')

    # Override the __unicode__() method to return out something meaningful!
    def __unicode__(self):
        return self.user.username