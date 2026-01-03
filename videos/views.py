from django.shortcuts import render, get_object_or_404, redirect
from .models import Video, Comment
from .forms import VideoUploadForm, CommentForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login
from django.db.models import Q
from django.http import JsonResponse, HttpResponseBadRequest
import json
from channels.models import Channel, Subscription
from django.views.decorators.http import require_POST
from .models import Playlist, PlaylistItem, WatchLater
from django.contrib import messages
from django.views.decorators.http import require_POST

@login_required
def watch_later(request):
	items = WatchLater.objects.filter(user=request.user).select_related('video').order_by('-added_at')
	videos = [w.video for w in items]
	return render(request, 'watch_later.html', {'videos': videos})


@login_required
@require_POST
def toggle_watch_later(request, pk):
	video = get_object_or_404(Video, pk=pk)
	obj, created = WatchLater.objects.get_or_create(user=request.user, video=video)
	if not created:
		obj.delete()
		messages.success(request, 'Removed from Watch Later')
	else:
		messages.success(request, 'Added to Watch Later')
	return redirect('video_detail', pk=pk)


@login_required
def create_playlist(request):
	if request.method == 'POST':
		title = request.POST.get('title')
		desc = request.POST.get('description', '')
		is_public = bool(request.POST.get('is_public'))
		if title:
			pl = Playlist.objects.create(owner=request.user, title=title, description=desc, is_public=is_public)
			return redirect('playlist_detail', pk=pl.pk)
	return render(request, 'create_playlist.html')


def playlist_detail(request, pk):
	playlist = get_object_or_404(Playlist, pk=pk)
	items = playlist.items.select_related('video')
	return render(request, 'playlist_detail.html', {'playlist': playlist, 'items': items})


def index(request):
	"""Homepage showing a grid of videos."""
	# Use explicit `is_short` flag so creators can mark shorts; fall back to recent if none
	shorts_qs = Video.objects.filter(is_short=True).order_by('-uploaded_at')
	if not shorts_qs.exists():
		shorts_qs = Video.objects.order_by('-uploaded_at')[:6]
	shorts = list(shorts_qs[:6])
	# Regular videos exclude shorts
	videos = list(Video.objects.filter(is_short=False).order_by('-uploaded_at'))
	return render(request, 'home.html', {'videos': videos, 'shorts': shorts})


def subscriptions_feed(request):
	"""Show videos from channels the user is subscribed to."""
	if not request.user.is_authenticated:
		return redirect('index')
	# get channels the user subscribes to
	subs = request.user.subscriptions.values_list('channel__user', flat=True)
	videos = Video.objects.filter(channel__in=subs).order_by('-uploaded_at')
	return render(request, 'subscriptions.html', {'videos': videos})


def video_detail(request, pk):
	video = get_object_or_404(Video, pk=pk)
	# increment views
	video.views += 1
	video.save()

	# handle new comment submission
	comment_form = CommentForm()
	if request.method == 'POST' and request.user.is_authenticated and 'comment_submit' in request.POST:
		comment_form = CommentForm(request.POST)
		if comment_form.is_valid():
			Comment.objects.create(video=video, author=request.user, text=comment_form.cleaned_data['text'])
			return redirect('video_detail', pk=video.pk)

	# recommended videos for the right column
	recommended = Video.objects.exclude(pk=video.pk)[:8]
	# top-level comments (avoid complex lookups in templates)
	top_comments = video.comments.filter(parent__isnull=True).order_by('-created_at')
	return render(request, 'video_detail.html', {
		'video': video,
		'comment_form': comment_form,
		'recommended': recommended,
		'top_comments': top_comments,
	})


def search(request):
	q = request.GET.get('q', '')
	results = []
	if q:
		results = Video.objects.filter(Q(title__icontains=q) | Q(description__icontains=q))
	return render(request, 'search_results.html', {'query': q, 'results': results})


@login_required
def upload(request):
	if request.method == 'POST':
		form = VideoUploadForm(request.POST, request.FILES)
		if form.is_valid():
			video = form.save(commit=False)
			video.channel = request.user
			video.save()
			return redirect('video_detail', pk=video.pk)
	else:
		form = VideoUploadForm()
	return render(request, 'upload.html', {'form': form})


def signup(request):
	if request.method == 'POST':
		form = UserCreationForm(request.POST)
		if form.is_valid():
			user = form.save()
			auth_login(request, user)
			return redirect('index')
	else:
		form = UserCreationForm()
	return render(request, 'registration/signup.html', {'form': form})


@login_required
def toggle_like(request, pk):
	video = get_object_or_404(Video, pk=pk)
	user = request.user
	if user in video.likes.all():
		video.likes.remove(user)
	else:
		video.likes.add(user)
	return redirect('video_detail', pk=pk)


@login_required
def like_ajax(request, pk):
	"""AJAX endpoint to toggle like and return JSON with new count and status."""
	if request.method != 'POST':
		return HttpResponseBadRequest('POST required')
	video = get_object_or_404(Video, pk=pk)
	user = request.user
	if user in video.likes.all():
		video.likes.remove(user)
		liked = False
	else:
		video.likes.add(user)
		liked = True
	return JsonResponse({'liked': liked, 'count': video.likes.count()})


@login_required
def comment_ajax(request, pk):
	"""AJAX endpoint to post a comment and return the comment as JSON."""
	if request.method != 'POST':
		return HttpResponseBadRequest('POST required')
	video = get_object_or_404(Video, pk=pk)
	# Accept JSON or form-encoded
	data = {}
	if request.content_type == 'application/json':
		try:
			data = json.loads(request.body.decode())
		except Exception:
			return HttpResponseBadRequest('Invalid JSON')
	else:
		data = request.POST

	text = data.get('text')
	parent_id = data.get('parent')
	if not text or not text.strip():
		return HttpResponseBadRequest('Empty comment')

	parent = None
	if parent_id:
		try:
			parent = Comment.objects.get(pk=int(parent_id), video=video)
		except Exception:
			return HttpResponseBadRequest('Invalid parent')

	comment = Comment.objects.create(video=video, author=request.user, text=text.strip(), parent=parent)
	return JsonResponse({
		'author': comment.author.username,
		'text': comment.text,
		'created_at': comment.created_at.isoformat(),
		'id': comment.id,
		'parent': comment.parent.id if comment.parent else None,
	})


@login_required
@require_POST
def flag_comment_ajax(request, pk):
	# flag comment (increment flagged_count). Admins can review.
	comment = get_object_or_404(Comment, pk=pk)
	comment.flagged_count = comment.flagged_count + 1
	comment.save()
	return JsonResponse({'flagged': True, 'flagged_count': comment.flagged_count})
