# Import core DRF modules
from rest_framework import serializers
from django.db.models import Avg, Count

# Import application models
from .models import City, Attraction, CityRating, AttractionRating, Bookmark

# City Serializer
class CitySerializer(serializers.ModelSerializer):
    """
    Serializer for City model: Converts city data to JSON format for frontend display
    Includes aggregated rating statistics (average rating, rating count)
    """
    # Add read-only aggregated fields (calculated via ORM annotations)
    avg_rating = serializers.FloatField(read_only=True)
    rating_count = serializers.IntegerField(read_only=True)
    # Nested serializer for associated attractions (optional, for detail views)
    attractions = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = City
        fields = ['id', 'name', 'description', 'cover_image',
                  'created_at', 'updated_at', 'avg_rating', 'rating_count', 'attractions','image_url']
        read_only_fields = ['id', 'created_at', 'updated_at']  # Auto-generated fields

    # Custom method: Serialize associated attractions (basic info only)
    def get_attractions(self, obj):
        # Annotate attractions with rating stats before serialization
        attractions = obj.attractions.annotate(
            avg_rating=Avg('ratings__rating', default=0),
            rating_count=Count('ratings__rating', default=0)
        )
        return AttractionMinimalSerializer(attractions, many=True).data

# Attraction Minimal Serializer
class AttractionMinimalSerializer(serializers.ModelSerializer):
    """
    Minimal Attraction Serializer: For nested display in city lists (reduced data payload)
    """
    avg_rating = serializers.FloatField(read_only=True)
    rating_count = serializers.IntegerField(read_only=True)
    city_name = serializers.CharField(source='city.name', read_only=True)  # Nested city name

    class Meta:
        model = Attraction
        fields = ['id', 'name', 'city_name', 'cover_image', 'avg_rating', 'rating_count','image_url']

# Attraction Detail Serializer
class AttractionDetailSerializer(serializers.ModelSerializer):
    """
    Detailed Attraction Serializer: For attraction detail pages (full data + stats)
    """
    avg_rating = serializers.FloatField(read_only=True)
    rating_count = serializers.IntegerField(read_only=True)
    city_name = serializers.CharField(source='city.name', read_only=True)
    is_bookmarked = serializers.BooleanField(read_only=True)  # For logged-in user state

    class Meta:
        model = Attraction
        fields = ['id', 'name', 'city', 'city_name', 'description',
                  'official_url', 'cover_image', 'avg_rating', 'rating_count', 'is_bookmarked','image_url']
        read_only_fields = ['id']

# City Rating Serializer
class CityRatingSerializer(serializers.ModelSerializer):
    """
    Serializer for City Rating submissions: Validates and serializes rating data
    Auto-associates current user
    """
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    city_name = serializers.CharField(source='city.name', read_only=True)

    class Meta:
        model = CityRating
        fields = ['id', 'user', 'city', 'city_name', 'rating', 'created_at']
        read_only_fields = ['id', 'created_at']
        validators = []   # <- important: disable unique_together auto validation

    def validate_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Rating must be between 1 and 5 stars")
        return value

    def create(self, validated_data):
        user = validated_data['user']
        city = validated_data['city']
        rating, created = CityRating.objects.update_or_create(
            user=user,
            city=city,
            defaults={'rating': validated_data['rating']}
        )
        return rating
    
# Attraction Rating Serializer
class AttractionRatingSerializer(serializers.ModelSerializer):
    """
    Serializer for Attraction Rating submissions: Mirrors CityRatingSerializer logic
    """
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    attraction_name = serializers.CharField(source='attraction.name', read_only=True)
    city_name = serializers.CharField(source='attraction.city.name', read_only=True)

    class Meta:
        model = AttractionRating
        fields = ['id', 'user', 'attraction', 'attraction_name',
                  'city_name', 'rating', 'created_at']
        read_only_fields = ['id', 'created_at']
        validators = []   # <- important: disable unique_together auto validation

    def validate_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Rating must be between 1 and 5 stars")
        return value

    def create(self, validated_data):
        user = validated_data['user']
        attraction = validated_data['attraction']
        rating, created = AttractionRating.objects.update_or_create(
            user=user,
            attraction=attraction,
            defaults={'rating': validated_data['rating']}
        )
        return rating

# Bookmark Serializer
class BookmarkSerializer(serializers.ModelSerializer):
    """
    Serializer for Bookmark operations: Handles add/remove bookmark requests
    Returns status and message for frontend JS feedback
    """
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    attraction_name = serializers.CharField(source='attraction.name', read_only=True)
    city_name = serializers.CharField(source='attraction.city.name', read_only=True)
    # Custom fields for operation status (not stored in DB)
    status = serializers.CharField(read_only=True)
    message = serializers.CharField(read_only=True)

    class Meta:
        model = Bookmark
        fields = ['id', 'user', 'attraction', 'attraction_name',
                  'city_name', 'created_at', 'status', 'message']
        read_only_fields = ['id', 'created_at']

    # Custom create method: Toggle bookmark (add/remove)
    def create(self, validated_data):
        user = validated_data['user']
        attraction = validated_data['attraction']

        # Check if bookmark already exists
        bookmark_exists = Bookmark.objects.filter(user=user, attraction=attraction).exists()

        if bookmark_exists:
            # Remove existing bookmark
            Bookmark.objects.filter(user=user, attraction=attraction).delete()
            return {
                'status': 'unbookmarked',
                'message': 'Successfully removed from bookmarks',
                'attraction': attraction,
                'user': user
            }
        else:
            # Create new bookmark
            bookmark = Bookmark.objects.create(**validated_data)
            # Add custom response fields
            bookmark.status = 'bookmarked'
            bookmark.message = 'Successfully added to bookmarks'
            return bookmark

# Bookmark List Serializer
class BookmarkListSerializer(serializers.ModelSerializer):
    """
    Serializer for Bookmark list views: Displays user's saved attractions with details
    """
    attraction = AttractionMinimalSerializer(read_only=True)  # Nested attraction data
    city_name = serializers.CharField(source='attraction.city.name', read_only=True)

    class Meta:
        model = Bookmark
        fields = ['id', 'attraction', 'city_name', 'created_at']
        read_only_fields = ['id', 'created_at']

# City Rating Stats Serializer
class CityRatingStatsSerializer(serializers.Serializer):
    """
    Serializer for City Rating statistics: Returns aggregated rating data
    Used for dynamic frontend updates (no DB model association)
    """
    avg_rating = serializers.FloatField()
    rating_count = serializers.IntegerField()
    message = serializers.CharField()
    status = serializers.CharField()

# Attraction Rating Stats Serializer
class AttractionRatingStatsSerializer(serializers.Serializer):
    """
    Serializer for Attraction Rating statistics: Mirrors CityRatingStatsSerializer
    """
    avg_rating = serializers.FloatField()
    rating_count = serializers.IntegerField()
    message = serializers.CharField()
    status = serializers.CharField()