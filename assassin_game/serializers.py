from assassin_game.models import Player, Game, Post, Like, Comment, CommentLike, UserGameStatus, Badge
from rest_framework import serializers
from django.contrib.auth.models import User


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ('id', 'status', 'name', 'game_picture',)


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ('year', 'profile_picture')


class PostSerializer(serializers.ModelSerializer):
    poster = serializers.PrimaryKeyRelatedField(many=False, read_only=True)
    killed = serializers.PrimaryKeyRelatedField(many=False, read_only=True)
    game = serializers.PrimaryKeyRelatedField(many=False, read_only=False, queryset=Game.objects.all())
    status = serializers.CharField(read_only=True)
    time_confirmed = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Post
        fields = ('id', 'post_video', 'post_thumbnail_image', 'caption', 'status', 'time_confirmed', 'poster', 'killed',
                  'game', 'longitude', 'latitude')


class UserGameStatusSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(many=False, read_only=True)
    target = serializers.PrimaryKeyRelatedField(many=False, read_only=True)
    game = serializers.PrimaryKeyRelatedField(many=False, read_only=True)

    class Meta:
        model = UserGameStatus
        fields = ('id', 'status', 'game', 'user', 'target')


class LikeSerializer(serializers.ModelSerializer):
    post = serializers.PrimaryKeyRelatedField(many=False, read_only=False, queryset=Post.objects.all())
    liker = serializers.PrimaryKeyRelatedField(many=False, read_only=True)

    class Meta:
        model = Like
        fields = ('id', 'post', 'liker')


class BadgeSerializer(serializers.ModelSerializer):
    game = serializers.PrimaryKeyRelatedField(many=False, read_only=False, queryset=Game.objects.all())
    user = serializers.PrimaryKeyRelatedField(many=False, read_only=True)

    class Meta:
        model = Badge
        fields = ('id', 'game', 'user', 'type')


class CommentSerializer(serializers.ModelSerializer):
    post = serializers.PrimaryKeyRelatedField(many=False, read_only=False, queryset=Post.objects.all())
    commenter = serializers.PrimaryKeyRelatedField(many=False, read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'post', 'commenter', 'text', 'time')


class CommentLikeSerializer(serializers.ModelSerializer):
    comment = serializers.PrimaryKeyRelatedField(many=False, read_only=False, queryset=Comment.objects.all())
    liker = serializers.PrimaryKeyRelatedField(many=False, read_only=True)

    class Meta:
        model = CommentLike
        fields = ('id', 'comment', 'liker')


class UserSerializer(serializers.ModelSerializer):
    player = PlayerSerializer(required=True)
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        player_data = validated_data.pop('player')
        user = User.objects.create_user(
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password'],
            email=validated_data['email'],
        )

        Player.objects.create(
            user=user,
            profile_picture=player_data['profile_picture'],
            year=player_data['year']
        )

        return user

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.password = validated_data.get('password', instance.password)
        instance.email = validated_data.get('email', instance.email)


        player_data = validated_data.pop('player')
        player = Player.objects.get(user=instance)
        player.year = player_data.get('year', player.year)
        player.profile_picture = player_data.get('profile_picture', player.profile_picture)

        instance.save()
        player.save()

        return instance


    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'password', 'player',)
