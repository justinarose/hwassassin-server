from rest_framework import viewsets
from rest_framework.response import Response
from assassin_game.models import Game, Post, UserGameStatus, Like, Comment, CommentLike, Badge
from assassin_game.serializers import (GameSerializer, UserSerializer, PostSerializer, UserGameStatusSerializer,
                                       LikeSerializer, CommentSerializer, CommentLikeSerializer, BadgeSerializer)
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.decorators import detail_route
from rest_framework import mixins
from rest_framework.exceptions import ValidationError
from django.utils import timezone


# pretty much done with game view set
class GameViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer

    @detail_route(methods=['post'])
    def join(self, request, pk=None):

        game = self.get_object()
        user = request.user

        if not user.is_authenticated():
            return Response({"Error": "User is not authenticated"}, status=status.HTTP_406_NOT_ACCEPTABLE)

        if game.status != 'r':
            return Response({"Error": "Game isn't in registration status"}, status=status.HTTP_406_NOT_ACCEPTABLE)

        existing = UserGameStatus.objects.filter(user=user, game=game)
        statuses = UserGameStatus.objects.filter(game=game)
        if existing.count() > 0:
            print('User already joined game')
            res = UserGameStatusSerializer(existing.first(), context={'request': request})
            return Response(res.data, status=status.HTTP_409_CONFLICT)

        elif statuses.count() == 0:
            print('Creating first user status')
            target = request.user
            s = UserGameStatus.objects.create(user=user, target=target, game=game, status='a')
            res = UserGameStatusSerializer(s, context={'request': request})
            return Response(res.data, status=status.HTTP_201_CREATED)

        else:
            print('Adding another user status')
            first = statuses.first()
            target = first.target
            first.target = user
            first.save()
            s = UserGameStatus.objects.create(user=user, target=target, game=game, status='a')
            res = UserGameStatusSerializer(s, context={'request': request})
            return Response(res.data, status=status.HTTP_201_CREATED)


# needs some work (especially token authentication and stuff)
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_fields = ['username']


# almost done (make sure corner case stuff like posting/verifying twice is good)
class PostViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    filter_fields = ['poster', 'killed', 'game', 'status']

    @detail_route(methods=['post'])
    def verify(self, request, pk=None):
        post = self.get_object()
        user = request.user

        if not user.is_authenticated() or user != post.killed:
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            poster_status = UserGameStatus.objects.filter(user=post.poster, game=post.game).first()
            killed_status = UserGameStatus.objects.filter(user=user, game=post.game).first()
            poster_status.target = killed_status.target
            killed_status.status = 'd'
            post.status = 'v'
            post.time_confirmed = timezone.now()
            poster_status.save()
            killed_status.save()
            post.save()
            res = PostSerializer(post)
            return Response(res.data, status=status.HTTP_202_ACCEPTED)

    @detail_route(methods=['post'])
    def deny(self, request, pk=None):
        post = self.get_object()
        user = request.user

        if not user.is_authenticated() or user != post.killed:
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            post.status = 'c'
            post.save()
            res = PostSerializer(post)
            return Response(res.data, status=status.HTTP_202_ACCEPTED)

    @detail_route(methods=['post'])
    def like(self, request, pk=None):
        post = self.get_object()
        user = request.user

        if not user.is_authenticated():
            return Response({"Error": "User is not authenticated"}, status=status.HTTP_406_NOT_ACCEPTABLE)

        existing = Like.objects.filter(post=post, liker=user)
        if existing.count() > 0:
            return Response({"Error": "User already liked post"}, status=status.HTTP_409_CONFLICT)
        else:
            like = Like.objects.create(post=post, liker=user)
            res = LikeSerializer(like)
            return Response(res.data, status=status.HTTP_202_ACCEPTED)

    @detail_route(methods=['post'])
    def unlike(self, request, pk=None):
        post = self.get_object()
        user = request.user

        if not user.is_authenticated():
            return Response({"Error": "User is not authenticated"}, status=status.HTTP_406_NOT_ACCEPTABLE)

        existing = Like.objects.filter(post=post, liker=user)

        if existing.count() == 0:
            return Response({"Error": "User hasn't liked post"}, status=status.HTTP_409_CONFLICT)
        else:
            existing.delete()
            return Response(status=status.HTTP_202_ACCEPTED)

    def perform_create(self, serializer):
        user = self.request.user

        if not user.is_authenticated():
            raise ValidationError('You need to log in')

        game = serializer.validated_data['game']
        user_status = UserGameStatus.objects.filter(user=user, game=game).first()
        if user_status is None or user_status.status != 'a':
            raise ValidationError('You are not alive')
        if game.status != 'p':
            raise ValidationError('The game is not in progress')

        killed = user_status.target
        stat = 'p'
        existing = Post.objects.filter(poster=user, killed=killed, status=stat)
        if existing.count() > 0:
            raise ValidationError('Previous kill still pending')

        killed_status = UserGameStatus.objects.filter(user=killed, game=game).first()
        killed_status.status = 'p'
        killed_status.save()
        serializer.save(poster=user, killed=killed, status=stat, time_confirmed=timezone.now())


# pretty much done (need to add tests)
class UserGameStatusViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = UserGameStatus.objects.all()
    serializer_class = UserGameStatusSerializer
    filter_fields = ['user', 'game', 'status']


# pretty much done (need to add tests)
class LikeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    filter_fields = ['post', 'liker']

    def perform_create(self, serializer):
        serializer.save(liker=self.request.user)


# pretty much done (need to add tests)
class CommentViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    filter_fields = ['post', 'commenter']

    @detail_route(methods=['post'])
    def like(self, request, pk=None):
        comment = self.get_object()
        user = request.user

        if not user.is_authenticated():
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)

        existing = CommentLike.objects.filter(comment=comment, liker=user)
        if existing.count() > 0:
            return Response(status=status.HTTP_409_CONFLICT)
        else:
            like = CommentLike.objects.create(comment=comment, liker=user)
            res = CommentLikeSerializer(like)
            return Response(res.data, status=status.HTTP_202_ACCEPTED)

    @detail_route(methods=['post'])
    def unlike(self, request, pk=None):
        comment = self.get_object()
        user = request.user

        if not user.is_authenticated():
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)

        existing = CommentLike.objects.filter(comment=comment, liker=user)

        if existing.count() == 0:
            return Response(status=status.HTTP_409_CONFLICT)
        else:
            existing.delete()
            return Response(status=status.HTTP_202_ACCEPTED)

    def perform_create(self, serializer):
        user = self.request.user

        if not user.is_authenticated():
            raise ValidationError('You need to log in')

        serializer.save(commenter=user)


# pretty much done (need to test)
class CommentLikeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CommentLike.objects.all()
    serializer_class = CommentLikeSerializer
    filter_fields = ['comment', 'liker']


class BadgeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Badge.objects.all()
    serializer_class = BadgeSerializer
    filter_fields = ['game', 'user', 'type']
