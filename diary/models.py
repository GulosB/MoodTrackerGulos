from django.db import models

class MoodTag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class DiaryEntry(models.Model):
    text = models.TextField()
    mood_tag = models.ForeignKey(MoodTag, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.created_at.strftime('%Y-%m-%d')} - {self.mood_tag}"

class MoodStat(models.Model):
    date = models.DateField(unique=True)
    positive_count = models.IntegerField(default=0)
    negative_count = models.IntegerField(default=0)
    neutral_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.date} - +:{self.positive_count} -:{self.negative_count} =:{self.neutral_count}"