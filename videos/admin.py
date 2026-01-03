from django.contrib import admin
from .models import Video, Comment


from .models import Playlist, PlaylistItem, WatchLater


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
	list_display = ('title', 'channel', 'uploaded_at', 'views', 'is_short')
	search_fields = ('title', 'description')
	list_filter = ('is_short', 'uploaded_at')
	actions = ['mark_as_short', 'unmark_as_short']

	def mark_as_short(self, request, queryset):
		updated = queryset.update(is_short=True)
		self.message_user(request, f'Marked {updated} videos as short')
	mark_as_short.short_description = 'Mark selected videos as Shorts'

	def unmark_as_short(self, request, queryset):
		updated = queryset.update(is_short=False)
		self.message_user(request, f'Unmarked {updated} videos')
	unmark_as_short.short_description = 'Unmark selected videos as Shorts'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
	list_display = ('video', 'author', 'created_at', 'parent', 'is_hidden', 'flagged_count')
	search_fields = ('text',)
	list_filter = ('is_hidden',)
	actions = ['hide_comments', 'unhide_comments']

	def hide_comments(self, request, queryset):
		updated = queryset.update(is_hidden=True)
		self.message_user(request, f'Hid {updated} comments')
	hide_comments.short_description = 'Hide selected comments'

	def unhide_comments(self, request, queryset):
		updated = queryset.update(is_hidden=False)
		self.message_user(request, f'Unhid {updated} comments')
	unhide_comments.short_description = 'Unhide selected comments'


@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
	list_display = ('title', 'owner', 'created_at', 'is_public')
	search_fields = ('title', 'owner__username')


@admin.register(PlaylistItem)
class PlaylistItemAdmin(admin.ModelAdmin):
	list_display = ('playlist', 'video', 'order')


@admin.register(WatchLater)
class WatchLaterAdmin(admin.ModelAdmin):
	list_display = ('user', 'video', 'added_at')
