from django.shortcuts import render
from django.views import View
from .forms import MotionForm, VoteForm

# Create your views here.

class MotionView(View):
    template_name = 'motion_create.html'
    form_class = MotionForm

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            form = self.form_class()

        context = {
            'form': form
        }
        return render(request, self.template_name, context)


class VoteView(View):
    template_name = 'vote_create.html'
    form_class = VoteForm

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            form = self.form_class()

        context = {
            'form': form
        }
        return render(request, self.template_name, context)