from rest_framework.routers import DefaultRouter

from .views import AuthorViewSet

router = DefaultRouter()
router.register("", AuthorViewSet, basename="author")

urlpatterns = router.urls
