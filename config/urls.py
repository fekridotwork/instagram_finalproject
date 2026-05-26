"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

from accounts.views import PublicProfileAPIView
from posts.views import ExploreAPIView, UserPostsAPIView

from .views import HealthCheckAPIView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/health/', HealthCheckAPIView.as_view(), name='api-health'),
    path('api/auth/', include("authentication.urls")),
    path("api/profile/", include("accounts.urls")),
    path('api/posts/', include("posts.urls")),
    path('api/', include("interactions.urls")),
    path('api/users/<str:username>/posts/', UserPostsAPIView.as_view(), name='user_posts'),
    path(
        "api/users/<str:username>/",
        PublicProfileAPIView.as_view(),
        name="public-profile",
    ),
    path("api/stories/", include("posts.story_urls")),
    path("api/search/", include("posts.search_urls")),
    path("api/direct/", include("direct.urls")),
    path("api/explore/", ExploreAPIView.as_view(), name="explore"),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)