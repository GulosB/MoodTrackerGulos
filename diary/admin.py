from django.contrib import admin
from .models import MoodTag, DiaryEntry, MoodStat

@admin.register(MoodTag)
class MoodTagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

@admin.register(DiaryEntry)
class DiaryEntryAdmin(admin.ModelAdmin):
    list_display = ('id', 'text_short', 'mood_tag', 'created_at')
    list_filter = ('mood_tag', 'created_at')

    def text_short(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_short.short_description = 'Текст'

@admin.register(MoodStat)
class MoodStatAdmin(admin.ModelAdmin):
    list_display = ('date', 'positive_count', 'negative_count', 'neutral_count')