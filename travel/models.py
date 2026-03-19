from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg


# City Model
class City(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    cover_image = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image_url = models.URLField(blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


# City Rating
class CityRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="city_ratings")
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="ratings")
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'city']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.city.name} ({self.rating})"


# Attraction Model
class Attraction(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="attractions")
    name = models.CharField(max_length=200)
    cover_image = models.URLField(blank=True)
    official_url = models.URLField(blank=True)
    description = models.TextField(blank=True) 
    image_url = models.URLField(blank=True) 


    def average_rating(self):
        avg = self.ratings.aggregate(Avg('rating'))['rating__avg']
        return avg if avg else 0

    def __str__(self):
        return self.name


# Attraction Rating
class AttractionRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="attraction_ratings")
    attraction = models.ForeignKey(Attraction, on_delete=models.CASCADE, related_name="ratings")
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'attraction']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.attraction.name} ({self.rating})"

# Bookmark
class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookmarks")
    attraction = models.ForeignKey(Attraction, on_delete=models.CASCADE, related_name="bookmarked_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "attraction")

    def __str__(self):
        return f"{self.user.username} -> {self.attraction.name}"