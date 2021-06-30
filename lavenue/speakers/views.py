from django.shortcuts import render

from .forms import InterventionForm, MotionForm, VoteForm

# Create your views here.

def intervention_create_view(request):
    form = InterventionForm(request.POST or None)
    if form.is_valid():
        form.save()
        form = InterventionForm()

    context = {
        'form': form
    }
    return render(request, "intervention_create.html", context)

def motion_create_view(request):
    form = MotionForm(request.POST or None)
    if form.is_valid():
        form.save()
        form = MotionForm()

    context = {
        'form': form
    }
    return render(request, "motion_create.html", context)

def vote_create_view(request):
    form = VoteForm(request.POST or None)
    if form.is_valid():
        form.save()
        form = VoteForm()

    context = {
        'form': form
    }
    return render(request, "vote_create.html", context)