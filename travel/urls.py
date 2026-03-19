from django.urls import path
from . import views
from .views import BookmarkListView, BookmarkToggleView

app_name = "travel"

urlpatterns = [
    path("", views.home, name="home"),
    path("cities/", views.CityListView.as_view(), name="cities"),
    path("attractions/", views.AttractionListView.as_view(), name="attractions"),
    path("city/<int:city_id>/", views.CityDetailView.as_view(), name="city_detail"),
    path("attractions/<int:attraction_id>/", views.AttractionDetailView.as_view(), name="attraction_detail"),

    path("api/cities/<int:city_id>/", views.city_attractions, name="city_attractions"),
    path("api/cities/filter/", views.CityFilterView.as_view(), name="city_filter"),

    path("bookmarks/", BookmarkListView.as_view(), name="bookmarks"),
    path("bookmarks/toggle/", BookmarkToggleView.as_view(), name="bookmark_toggle"),
    path("api/attraction/bookmark/toggle/", BookmarkToggleView.as_view(), name="bookmark_toggle_api"),

    path("api/city/rating/submit/", views.CityRatingSubmitView.as_view(), name="city_rating_submit"),
    path("api/attraction/rating/submit/", views.AttractionRatingSubmitView.as_view(), name="attraction_rating_submit"),

    path("protected/", views.protected, name="protected"),
]