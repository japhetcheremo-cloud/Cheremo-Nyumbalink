from django.db import models
from django.conf import settings

class BlogPost(models.Model):
    CATEGORY_CHOICES = [
        ('rental_tips', 'Rental Tips'),
        ('interior_design', 'Interior Design'),
        ('moving_guides', 'Moving Guides'),
        ('property_news', 'Property News'),
        ('investment', 'Real Estate Investment'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    content = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='blog_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

