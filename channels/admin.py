from django.contrib import admin
from .models import Channel, Subscription


@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ('user', 'display_name', 'created_at')
    search_fields = ('user__username', 'display_name')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('subscriber', 'channel', 'created_at')
    search_fields = ('subscriber__username', 'channel__user__username')
