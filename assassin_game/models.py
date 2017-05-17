from django.db import models
from django.contrib.auth.models import User


class Player(models.Model):
    year = models.CharField(max_length=4)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pictures/')

    def __str__(self):
        return '%s' % self.user.username


class Game(models.Model):
    STATUS_CHOICE = (
        ('r', "Registration"),
        ('p', "Progress"),
        ('c', "Completed"),
    )

    status = models.CharField(max_length=1, choices=STATUS_CHOICE)
    name = models.CharField(max_length=256)
    game_picture = models.ImageField(upload_to='game_pictures/')

    def __str__(self):
        return '%s' % self.name


class Post(models.Model):
    poster = models.ForeignKey(User, on_delete=models.CASCADE, related_name="kills")
    killed = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="posts")
    post_video = models.FileField(upload_to='post_videos/')
    post_thumbnail_image = models.ImageField(upload_to='post_thumbnail_image/')
    caption = models.TextField(default="")
    latitude = models.FloatField(default=34.140808)
    longitude = models.FloatField(default=-118.412303)

    POST_STATUS_CHOICE = (
        ('p', "Pending"),
        ('c', "Conflicting"),
        ('v', "Verified"),
        ('d', "Denied"),
    )

    status = models.CharField(max_length=1, choices=POST_STATUS_CHOICE)
    time_confirmed = models.DateTimeField()

    def __str__(self):
        return "%s killed %s" % (self.poster, self.killed)


class Like(models.Model):
    post = models.ForeignKey(Post, related_name="likes", on_delete=models.CASCADE)
    liker = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return "%s liked Post %s" % (self.liker, self.post.id)

    class Meta:
        unique_together = ('post', 'liker',)


class Comment(models.Model):
    post = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE)
    commenter = models.ForeignKey(User, related_name="comments", on_delete=models.CASCADE)
    text = models.TextField()
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '%s (Post %s): %s' % (self.commenter, self.post.id, self.text)


class CommentLike(models.Model):
    comment = models.ForeignKey(Comment, related_name="likes", on_delete=models.CASCADE)
    liker = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return "%s liked Comment %s" % (self.liker, self.comment.id)

    class Meta:
        unique_together = ('comment', 'liker',)


class UserGameStatus(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="game_status")
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    target = models.ForeignKey(User, on_delete=models.CASCADE)

    USER_STATUS_CHOICE = (
        ('a', "Alive"),
        ('p', "Pending"),
        ('d', "Dead"),
    )

    status = models.CharField(max_length=1, choices=USER_STATUS_CHOICE)

    def __str__(self):
        return "%s (Game %s): %s" % (self.user, self.game.id, self.status)

    class Meta:
        unique_together = ('user', 'game',)


class Badge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="badges")
    game = models.ForeignKey(Game, on_delete=models.CASCADE)

    BADGE_TYPE_CHOICE = (
        ('f', "First Blood"),
        ('3', "Three Kills One Day"),
        ('5', "Five Kills One Day"),
        ('w', "Winner!"),
        ('p', "Participation"),
        ('l', "Leaderboard"),
        ('t', "Top")
    )

    type = models.CharField(max_length=1, choices=BADGE_TYPE_CHOICE)

    def __str__(self):
        return "%s (Game %s): %s" % (self.type, self.game.id, self.type)


class Report(models.Model):
    post = models.ForeignKey(Post, related_name="reports", on_delete=models.CASCADE)
    reporter = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return "%s reported Post %s" % (self.reporter, self.post.id)

    class Meta:
        unique_together = ('reporter', 'post',)