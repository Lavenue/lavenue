from django.shortcuts import render
from django.views import View
from .forms import InterventionForm, MotionForm, VoteForm

# Create your views here.
class InterventionView(View):
    template_name = 'intervention_create.html'
    form_class = InterventionForm
    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            form = self.form_class()

        context = {
            'form': form
        }
        return render(request, self.template_name, context)