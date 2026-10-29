from django.urls import path
from .views import (
    BrandProfileListView,
    ThreadCreateView,
    ThreadRefineView,
    ThreadDetailView,
    ImageLibraryView,
    SelectImageView,
)

urlpatterns = [
    path("brand-profiles/", BrandProfileListView.as_view(), name="brand-profiles-list"),
    path("threads/", ThreadCreateView.as_view(), name="threads-create"),
    path("threads/<int:id>/refine/", ThreadRefineView.as_view(), name="threads-refine"),
    path("threads/<int:id>/", ThreadDetailView.as_view(), name="threads-detail"),
    path("images/", ImageLibraryView.as_view(), name="images-library"),
    path("images/<int:id>/select/", SelectImageView.as_view(), name="images-select"),
]