from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.http import is_safe_url
from django.conf import settings
from django.views import View
from django.db.models import Avg, Count

from .models import City, Attraction, Bookmark, CityRating, AttractionRating
from .forms import CityFilterForm
from .serializers import (
    CitySerializer,
    BookmarkListSerializer,
    CityRatingSerializer,
    AttractionRatingSerializer,
)


def home(request):
    return render(request, "travel/home.html")


def register(request):
    if request.user.is_authenticated:
        return redirect("travel:home")

    next_url = request.GET.get("next") or request.POST.get("next") or "/"

    # 只接受真正的路徑，例如 /、/cities/、/bookmarks/
    if not next_url.startswith("/"):
        next_url = "/"

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Welcome! Your account has been created.")

            if is_safe_url(next_url, allowed_hosts={request.get_host()}):
                return redirect(next_url)
            return redirect("travel:home")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserCreationForm()

    return render(request, "registration/register.html", {
        "form": form,
        "next": next_url,
    })


@login_required
def protected(request):
    return HttpResponse("You are logged in ✅")


def city_list(request):
    cities = City.objects.all()
    return render(request, "travel/city_list.html", {"cities": cities})


def city_attractions(request, city_id):
    city = get_object_or_404(City, id=city_id)
    min_rating = request.GET.get("min_rating")

    attractions = (
        Attraction.objects
        .filter(city=city)
        .annotate(
            avg_rating=Avg("ratings__rating"),
            rating_count=Count("ratings__rating")
        )
        .order_by("-avg_rating", "name")
    )

    if min_rating:
        try:
            min_rating = float(min_rating)
            attractions = attractions.filter(avg_rating__gte=min_rating)
        except ValueError:
            pass

    data = []
    for a in attractions:
        data.append({
            "id": a.id,
            "name": a.name,
            "image": a.image_url,
            "url": a.official_url,
            "rating": a.avg_rating if a.avg_rating else 0,
            "rating_count": a.rating_count,
        })

    return JsonResponse({"attractions": data})


def attraction_detail(request, attraction_id):
    attraction = get_object_or_404(Attraction, id=attraction_id)
    return render(request, "travel/attraction_detail.html", {"attraction": attraction})


class CityListView(View):
    def get(self, request):
        form = CityFilterForm(request.GET)

        if form.is_valid():
            cities = form.filter_cities()
        else:
            cities = City.objects.annotate(
                avg_rating=Avg("ratings__rating"),
                rating_count=Count("ratings__rating")
            ).order_by("-avg_rating", "name")

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            serializer = CitySerializer(cities, many=True)
            return JsonResponse({"cities": serializer.data})

        context = {
            "cities": cities,
            "filter_form": form,
            "user": request.user,
        }
        return render(request, "travel/cities.html", context)


class CityDetailView(View):
    def get(self, request, city_id):
        city = get_object_or_404(City, id=city_id)
        attractions = Attraction.objects.filter(city=city).annotate(
            avg_rating=Avg("ratings__rating"),
            rating_count=Count("ratings__rating")
        ).order_by("-avg_rating", "name")

        user_rating = None
        if request.user.is_authenticated:
            user_rating = CityRating.objects.filter(user=request.user, city=city).first()

        city_stats = city.ratings.aggregate(
            avg_rating=Avg("rating"),
            rating_count=Count("rating")
        )

        context = {
            "city": city,
            "attractions": attractions,
            "user_rating": user_rating.rating if user_rating else 0,
            "avg_rating": round(city_stats["avg_rating"], 1) if city_stats["avg_rating"] else 0,
            "rating_count": city_stats["rating_count"],
            "user": request.user,
        }
        return render(request, "travel/city_detail.html", context)


class AttractionDetailView(View):
    template_name = "travel/attraction_detail.html"

    def get(self, request, attraction_id):
        attraction = get_object_or_404(Attraction, id=attraction_id)

        avg_rating = AttractionRating.objects.filter(
            attraction=attraction
        ).aggregate(avg=Avg("rating"))["avg"] or 0

        rating_count = AttractionRating.objects.filter(
            attraction=attraction
        ).count()

        user_rating_obj = None
        is_bookmarked = False

        if request.user.is_authenticated:
            user_rating_obj = AttractionRating.objects.filter(
                user=request.user,
                attraction=attraction
            ).first()

            is_bookmarked = Bookmark.objects.filter(
                user=request.user,
                attraction=attraction
            ).exists()

        context = {
            "attraction": attraction,
            "avg_rating": round(avg_rating, 1),
            "rating_count": rating_count,
            "user_rating": user_rating_obj.rating if user_rating_obj else 0,
            "is_bookmarked": is_bookmarked,
        }

        return render(request, self.template_name, context)


class BookmarkListView(LoginRequiredMixin, View):
    login_url = "login"

    def get(self, request, *args, **kwargs):
        bookmarks = (
            Bookmark.objects
            .filter(user=request.user)
            .select_related("attraction", "attraction__city")
            .order_by("-created_at")
        )

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            serializer = BookmarkListSerializer(bookmarks, many=True)
            return JsonResponse(
                {
                    "status": "success",
                    "count": bookmarks.count(),
                    "bookmarks": serializer.data,
                },
                status=200
            )

        context = {
            "bookmarks": bookmarks,
        }
        return render(request, "travel/bookmarks.html", context)


class BookmarkToggleView(LoginRequiredMixin, View):
    login_url = "login"

    def post(self, request, *args, **kwargs):
        attraction_id = request.POST.get("attraction") or kwargs.get("attraction_id")

        if not attraction_id:
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Attraction ID is required."
                },
                status=400
            )

        attraction = get_object_or_404(Attraction, pk=attraction_id)

        bookmark, created = Bookmark.objects.get_or_create(
            user=request.user,
            attraction=attraction
        )

        if created:
            action = "added"
            message = "Bookmark added successfully."
            is_bookmarked = True
        else:
            bookmark.delete()
            action = "removed"
            message = "Bookmark removed successfully."
            is_bookmarked = False

        return JsonResponse(
            {
                "status": "success",
                "action": action,
                "message": message,
                "attraction_id": attraction.id,
                "is_bookmarked": is_bookmarked,
            },
            status=200
        )

    def get(self, request, *args, **kwargs):
        return JsonResponse(
            {
                "status": "error",
                "message": "GET method is not allowed for this endpoint."
            },
            status=405
        )


class CityRatingSubmitView(LoginRequiredMixin, View):
    def post(self, request):
        serializer = CityRatingSerializer(data=request.POST, context={"request": request})

        if serializer.is_valid():
            serializer.save()

            city = serializer.validated_data["city"]
            stats = city.ratings.aggregate(
                avg_rating=Avg("rating"),
                rating_count=Count("rating")
            )

            return JsonResponse({
                "status": "success",
                "message": "Rating submitted successfully",
                "avg_rating": round(stats["avg_rating"], 1) if stats["avg_rating"] else 0,
                "rating_count": stats["rating_count"],
            }, status=200)

        return JsonResponse({
            "status": "error",
            "errors": serializer.errors,
            "message": "Failed to submit rating"
        }, status=400)


class AttractionRatingSubmitView(LoginRequiredMixin, View):
    def post(self, request):
        serializer = AttractionRatingSerializer(data=request.POST, context={"request": request})

        if serializer.is_valid():
            serializer.save()

            attraction = serializer.validated_data["attraction"]
            stats = attraction.ratings.aggregate(
                avg_rating=Avg("rating"),
                rating_count=Count("rating")
            )

            return JsonResponse({
                "status": "success",
                "message": "Attraction rating submitted successfully",
                "avg_rating": round(stats["avg_rating"], 1) if stats["avg_rating"] else 0,
                "rating_count": stats["rating_count"],
            }, status=200)

        return JsonResponse({
            "status": "error",
            "errors": serializer.errors,
            "message": "Failed to submit attraction rating"
        }, status=400)


class CityFilterView(View):
    def get(self, request):
        form = CityFilterForm(request.GET)

        if form.is_valid():
            cities = form.filter_cities()
            serializer = CitySerializer(cities, many=True)
            return JsonResponse({"cities": serializer.data})

        return JsonResponse({
            "status": "error",
            "errors": form.errors,
            "message": "Filter validation failed"
        }, status=400)


class CityAttractionsAPIView(View):
    def get(self, request, city_id):
        city = get_object_or_404(City, id=city_id)
        min_rating = request.GET.get("min_rating")

        attractions = (
            Attraction.objects
            .filter(city=city)
            .annotate(
                avg_rating=Avg("ratings__rating"),
                rating_count=Count("ratings__rating")
            )
            .order_by("-avg_rating", "name")
        )

        if min_rating:
            try:
                min_rating = float(min_rating)
                attractions = attractions.filter(avg_rating__gte=min_rating)
            except ValueError:
                pass

        data = [
            {
                "id": a.id,
                "name": a.name,
                "image": a.image_url,
                "url": a.official_url,
                "rating": a.avg_rating or 0,
                "rating_count": a.rating_count,
            }
            for a in attractions
        ]

        return JsonResponse({"attractions": data})


class AttractionListView(View):
    def get(self, request):
        name_query = request.GET.get("name", "").strip()
        min_rating = request.GET.get("min_rating", "").strip()

        attractions = (
            Attraction.objects
            .select_related("city")
            .annotate(
                avg_rating=Avg("ratings__rating"),
                rating_count=Count("ratings__rating")
            )
            .order_by("-avg_rating", "name")
        )

        if name_query:
            attractions = attractions.filter(name__icontains=name_query)

        if min_rating:
            try:
                attractions = attractions.filter(avg_rating__gte=float(min_rating))
            except ValueError:
                pass

        return render(request, "travel/attractions.html", {
            "attractions": attractions,
            "name_query": name_query,
            "min_rating": min_rating,
        })