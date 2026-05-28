from django.shortcuts import render, redirect
from .models import DiaryEntry, MoodTag, MoodStat
from .forms import DiaryEntryForm
from datetime import date
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
from django.utils import timezone

def analyze_mood(text):
    positive_words = ['радость', 'отлично', 'хорошо', 'супер', 'класс', 'счастье', 'люблю', 'прекрасно']
    negative_words = ['грусть', 'плохо', 'устал', 'кошмар', 'надоело', 'больно', 'страшно', 'ужасно']
    
    pos_count = sum(1 for word in positive_words if word in text.lower())
    neg_count = sum(1 for word in negative_words if word in text.lower())
    
    if pos_count > neg_count:
        return MoodTag.objects.get_or_create(name='Позитив')[0]
    elif neg_count > pos_count:
        return MoodTag.objects.get_or_create(name='Негатив')[0]
    else:
        return MoodTag.objects.get_or_create(name='Нейтрально')[0]

def update_mood_stats(entry_date):
    stats, _ = MoodStat.objects.get_or_create(date=entry_date)
    
    positive = DiaryEntry.objects.filter(
        created_at__date=entry_date,
        mood_tag__name='Позитив'
    ).count()
    negative = DiaryEntry.objects.filter(
        created_at__date=entry_date,
        mood_tag__name='Негатив'
    ).count()
    neutral = DiaryEntry.objects.filter(
        created_at__date=entry_date,
        mood_tag__name='Нейтрально'
    ).count()
    
    stats.positive_count = positive
    stats.negative_count = negative
    stats.neutral_count = neutral
    stats.save()

def index(request):
    if request.method == 'POST':
        form = DiaryEntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.mood_tag = analyze_mood(entry.text)
            entry.save()
            update_mood_stats(entry.created_at.date())
            return redirect('statistics')
    else:
        form = DiaryEntryForm()
    
    return render(request, 'index.html', {'form': form})

def statistics(request):
    stats = MoodStat.objects.all().order_by('date')
    
    dates = []
    mood_scores = []
    
    for stat in stats:
        total = stat.positive_count + stat.negative_count + stat.neutral_count
        if total > 0:
            score = (stat.positive_count * 1 + stat.negative_count * (-1) + stat.neutral_count * 0) / total
        else:
            score = 0
        
        dates.append(stat.date.strftime('%Y-%m-%d'))
        mood_scores.append(score)
    
    if len(dates) < 3:
        smooth_dates = dates
        smooth_scores = mood_scores
        use_smooth = False
    else:
        from scipy.interpolate import make_interp_spline
        import numpy as np
        x = np.arange(len(dates))
        spline = make_interp_spline(x, mood_scores, k=2)
        x_smooth = np.linspace(0, len(dates) - 1, 300)
        smooth_scores = spline(x_smooth)
        smooth_indexes = np.linspace(0, len(dates) - 1, 300)
        smooth_dates = []
        for idx in smooth_indexes:
            nearest = int(round(idx))
            if 0 <= nearest < len(dates):
                smooth_dates.append(dates[nearest])
            else:
                smooth_dates.append(dates[0])
        use_smooth = True
    
    plt.figure(figsize=(10, 5))
    
    if use_smooth:
        plt.plot(smooth_dates, smooth_scores, linestyle='-', linewidth=2, color='purple', label='Настроение')
        plt.scatter(dates, mood_scores, color='purple', zorder=5)
    else:
        plt.plot(dates, mood_scores, marker='o', linestyle='-', linewidth=2, color='purple', label='Настроение')
    
    plt.axhline(y=0, color='gray', linestyle='--', linewidth=1)
    
    plt.fill_between(dates, 0, mood_scores, where=[s > 0 for s in mood_scores], color='green', alpha=0.3, interpolate=True)
    plt.fill_between(dates, 0, mood_scores, where=[s < 0 for s in mood_scores], color='red', alpha=0.3, interpolate=True)
    
    plt.xlabel('Дата')
    plt.ylabel('Оценка настроения')
    plt.title('Динамика настроения')
    plt.legend()
    plt.xticks(rotation=45, ha='right')
    plt.grid(True, linestyle='--', alpha=0.5)
    
    ax = plt.gca()
    ax.set_ylim(-1.2, 1.2)
    ax.yaxis.set_major_locator(plt.MultipleLocator(0.5))
    
    plt.tight_layout()
    
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    graph = base64.b64encode(buffer.getvalue()).decode()
    buffer.close()
    plt.close()
    
    return render(request, 'statistics.html', {'graph': graph, 'stats': stats})