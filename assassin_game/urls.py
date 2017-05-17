from django.conf.urls import url, include
from assassin_game import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'games', views.GameViewSet)
router.register(r'users', views.UserViewSet)
router.register(r'posts', views.PostViewSet)
router.register(r'statuses', views.UserGameStatusViewSet)
router.register(r'likes', views.LikeViewSet)
router.register(r'comments', views.CommentViewSet)
router.register(r'comment-likes', views.CommentLikeViewSet)
router.register(r'badges', views.BadgeViewSet)
router.register(r'reports', views.ReportViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
]
