from django.contrib import admin
from assassin_game.models import Game, Player, Post, Like, Comment, CommentLike, UserGameStatus


# Register your models here.
admin.site.register(Game)
admin.site.register(Player)
admin.site.register(Post)
admin.site.register(Like)
admin.site.register(Comment)
admin.site.register(CommentLike)
admin.site.register(UserGameStatus)