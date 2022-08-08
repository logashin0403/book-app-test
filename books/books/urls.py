from django.conf import settings
from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework.routers import SimpleRouter

from store.views import BookViewSet, auth, UserBookRelationView

router = SimpleRouter()

router.register(r"book", viewset=BookViewSet)
router.register(r"book-relation", UserBookRelationView)

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path('', include('social_django.urls', namespace='social')),
    path('auth/', auth)
]

urlpatterns += router.urls

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls))
    ] + urlpatterns
