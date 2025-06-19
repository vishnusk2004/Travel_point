from django.db import models
import json
from django.db.models import Q

# Create your models here.

class Article(models.Model):
    url = models.URLField(unique=True)
    title = models.CharField(max_length=512)
    author = models.CharField(max_length=256, blank=True, null=True)
    author_title = models.CharField(max_length=256, blank=True, null=True)
    date_published = models.CharField(max_length=64, blank=True, null=True)
    last_modified = models.CharField(max_length=64, blank=True, null=True)
    content = models.TextField()
    featured_image = models.URLField(blank=True, null=True)
    image_credit = models.CharField(max_length=256, blank=True, null=True)
    categories = models.CharField(max_length=512, blank=True, null=True)
    seo_description = models.TextField(blank=True, null=True)
    reading_time = models.CharField(max_length=32, blank=True, null=True)
    scrape_timestamp = models.CharField(max_length=64, blank=True, null=True)
    rewritten_content = models.TextField(blank=True, null=True)
    structured_content = models.JSONField(blank=True, null=True)

    def __str__(self):
        return self.title

    def get_related_articles(self):
        # Get articles from the same category or with similar titles
        query = Q()
        
        # Add category filter if categories exist
        if self.categories:
            query |= Q(categories__icontains=self.categories)
        
        # Add title filter if title exists
        if self.title:
            first_word = self.title.split()[0] if self.title.split() else ''
            if first_word:
                query |= Q(title__icontains=first_word)
        
        # If no valid filters, return recent articles
        if not query:
            return Article.objects.exclude(id=self.id).order_by('-date_published')[:2]
        
        return Article.objects.filter(query).exclude(id=self.id)[:2]
