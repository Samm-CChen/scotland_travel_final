# Import core Django form modules
from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Avg, Count

# Import application models
from .models import CityRating, AttractionRating, Bookmark, City, Attraction

# City Rating Form
class CityRatingForm(forms.ModelForm):
    """
    City Rating Form: Validates user rating data for cities (1-5 stars)
    Associated View: CityRatingSubmitView
    Purpose: Backend fallback validation to prevent bypassing front-end JS checks
    """
    # Explicitly define rating field with valid options (1-5 stars) for front-end star selector
    rating = forms.IntegerField(
        label='City Rating',
        widget=forms.HiddenInput(),  # Hidden field (selected via front-end star component)
        min_value=1,
        max_value=5,
        error_messages={
            'min_value': 'Rating must be at least 1 star',
            'max_value': 'Rating cannot exceed 5 stars',
            'required': 'Rating is required'
        }
    )

    class Meta:
        model = CityRating  # Associate with CityRating model
        fields = ['city', 'rating']  # Fields to validate
        widgets = {
            'city': forms.HiddenInput()  # City ID passed from front-end (hidden display)
        }

    # Custom validation: Ensure strict 1-5 star rating range (fallback check)
    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if not (1 <= rating <= 5):
            raise ValidationError('Rating must be between 1 and 5 stars')
        return rating

    # Bind user during initialization (prevent front-end user ID transmission for security)
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    # Override save method: Auto-associate current user and prevent duplicate ratings
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.user = self.user  # Bind current logged-in user

        if commit:
            # Use update_or_create to avoid duplicate ratings (matches ER model unique constraint)
            CityRating.objects.update_or_create(
                user=self.user,
                city=instance.city,
                defaults={'rating': instance.rating}
            )
        return instance

# Attraction Rating Form
class AttractionRatingForm(forms.ModelForm):
    """
    Attraction Rating Form: Validates user rating data for attractions (1-5 stars)
    Associated View: AttractionRatingSubmitView
    Purpose: Backend fallback validation, paired with front-end form-validator.js
    """
    rating = forms.IntegerField(
        label='Attraction Rating',
        widget=forms.HiddenInput(),
        min_value=1,
        max_value=5,
        error_messages={
            'min_value': 'Rating must be at least 1 star',
            'max_value': 'Rating cannot exceed 5 stars',
            'required': 'Rating is required'
        }
    )

    class Meta:
        model = AttractionRating
        fields = ['attraction', 'rating']
        widgets = {
            'attraction': forms.HiddenInput()
        }

    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if not (1 <= rating <= 5):
            raise ValidationError('Rating must be between 1 and 5 stars')
        return rating

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.user = self.user

        if commit:
            AttractionRating.objects.update_or_create(
                user=self.user,
                attraction=instance.attraction,
                defaults={'rating': instance.rating}
            )
        return instance

# Bookmark Form (Minimal Validation)
class BookmarkForm(forms.ModelForm):
    """
    Bookmark Form: Validates legitimacy of bookmark operations (valid attraction, logged-in user)
    Associated View: BookmarkToggleView
    Purpose: Prevent bookmarking non-existent attractions and enhance operational security
    """
    class Meta:
        model = Bookmark
        fields = ['attraction']
        widgets = {
            'attraction': forms.HiddenInput()
        }

    # Custom validation: Ensure attraction exists
    def clean_attraction(self):
        attraction = self.cleaned_data.get('attraction')
        if not Attraction.objects.filter(id=attraction.id).exists():
            raise ValidationError('This attraction does not exist')
        return attraction

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    # Override save method: Implement one-click "bookmark/unbookmark" toggle
    def save(self, commit=True):
        attraction = self.cleaned_data.get('attraction')
        # Check if already bookmarked
        bookmark_exists = Bookmark.objects.filter(
            user=self.user,
            attraction=attraction
        ).exists()

        if bookmark_exists:
            # Delete if already bookmarked (unbookmark)
            Bookmark.objects.filter(user=self.user, attraction=attraction).delete()
            return {'status': 'unbookmarked', 'msg': 'Removed from bookmarks'}
        else:
            # Create if not bookmarked (add bookmark)
            instance = Bookmark(user=self.user, attraction=attraction)
            if commit:
                instance.save()
            return {'status': 'bookmarked', 'msg': 'Added to bookmarks'}

# City Filter Form (For Frontend Interaction)
class CityFilterForm(forms.Form):
    """
    City Filter Form: Used for frontend city list filtering (extended functionality)
    Supports fuzzy search by city name and filtering by minimum rating
    """
    city_name = forms.CharField(
        label='City Name',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by city name...',
            'id': 'id_city_name'
        })
    )

    min_rating = forms.FloatField(
        label='Minimum Rating',
        required=False,
        min_value=0,
        max_value=5,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.1',
            'min': '0',
            'max': '5',
            'id': 'id_min_rating'
        }),
        error_messages={
            'min_value': 'Minimum rating cannot be less than 0',
            'max_value': 'Minimum rating cannot exceed 5'
        }
    )

    def filter_cities(self):
        cities = City.objects.all().annotate(
            avg_rating=Avg('ratings__rating'),
            rating_count=Count('ratings__rating')
        )

        if self.cleaned_data.get('city_name'):
            cities = cities.filter(name__icontains=self.cleaned_data['city_name'])

        if self.cleaned_data.get('min_rating') is not None:
            cities = cities.filter(avg_rating__gte=self.cleaned_data['min_rating'])

        return cities.order_by('-avg_rating', 'name')