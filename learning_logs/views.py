from django.shortcuts import render
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import Topic, Entry
from .forms import TopicForm, EntryForm

# Create your views here.

def index(request):
    """The home page for Learning Log"""
    return render(request, 'learning_logs/index.html')

@login_required
def topics(request):
    """Shows all topics"""
    topics = Topic.objects.filter(owner=request.user).order_by('date_added')
    context = {'topics':topics}
    return render(request, 'learning_logs/topics.html', context)

@login_required
def topic(request, topic_id):
    topic = Topic.objects.get(id=topic_id)
    # Checks for appropriate user access
    check_topic_owner(topic.owner, request.user)

    entries = topic.entry_set.order_by('-date_added')
    context = {'topic': topic, 'entries': entries}

    return render(request, 'learning_logs/topic.html', context)

@login_required
def new_topic(request):
    # No data submitted, create new form
    if request.method != "POST":
        form = TopicForm()
    else:
    # POST data submitted, process data
        form = TopicForm(request.POST)
        if form.is_valid():
            new_topic = form.save(commit=False)
            new_topic.owner = request.user
            new_topic.save()
            return HttpResponseRedirect(reverse("learning_logs:topics"))
    context = {"form":form}
    return render(request, "learning_logs/new_topic.html", context)

@login_required
def new_entry(request, topic_id):
    """Add a new entry for a prticular topic"""
    topic = Topic.objects.get(id=topic_id)

    # No data submitted, create new form
    if request.method != "POST":
        form = EntryForm()
    # POST data submitted, process data
    else:
        form = EntryForm(data=request.POST)
        if form.is_valid():
            new_entry = form.save(commit=False)
            new_entry.topic = topic
            check_topic_owner(new_entry.topic.owner, request.user)
            new_entry.save()
            return HttpResponseRedirect(reverse("learning_logs:topic", args=[topic_id]))
    context = {"topic": topic, "form": form}
    return render(request, "learning_logs/new_entry.html", context)

@login_required
def edit_entry(request, entry_id):
    entry = Entry.objects.get(id=entry_id)
    topic = entry.topic

    # Protects user's entries from inappropriate access
    check_topic_owner(topic.owner, request.user)

    if request.method != "POST":
        form = EntryForm(instance=entry)
    else:
        form = EntryForm(instance=entry, data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("learning_logs:topic", args=[topic.id]))

    context = {
        "topic": topic, "entry": entry, "form": form
    }
    return render(request, "learning_logs/edit_entry.html", context)

def check_topic_owner(owner, user):
    if owner != user:
        raise Http404