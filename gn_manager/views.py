from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Entry
from django.contrib import messages
from .tables import EntryTable
from django_tables2 import RequestConfig
from django.urls import reverse_lazy
from .forms import EntryForm
from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView, BSModalDeleteView
from django.contrib.auth.decorators import login_required

@login_required
def manager(request):
    user = request.user
    if not user.is_active:
        messages.warning(request,"Your email has not been verified - your queries will not be scanned until it is verified. Visit your profile page to resend your verification email.",extra_tags='safe')
    if user.phone and not user.active_phone:
        messages.warning(request,"Your phone number has not been verified - you may not receive any text notifications until it is verified. Visit your profile page to resend your verification text.")
    table = EntryTable(Entry.objects.filter(user=user))
    table.order_by = "-id"
    RequestConfig(request,paginate={"per_page": 10}).configure(table)
    return render(request, 'gn_manager/manager.html',{'title':"Manager","table":table})

class EntryCreateView(BSModalCreateView):
    template_name = 'gn_manager/create.html'
    form_class = EntryForm
    success_message = 'Entry has been created.'
    success_url = reverse_lazy('manager')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class EntryEditView(BSModalUpdateView):
    model = Entry
    template_name = 'gn_manager/edit.html'
    form_class = EntryForm
    success_message = 'Entry has been updated.'
    success_url = reverse_lazy('manager')

    def dispatch(self, request, *args, **kwargs):
        if not Entry.objects.filter(pk=kwargs['pk']).exists():
            return HttpResponse(status=404)
        elif not Entry.objects.filter(user=request.user,pk=kwargs['pk']).exists():
            return HttpResponse(status=403)
        return super().dispatch(request, *args, **kwargs)

class EntryDeleteView(BSModalDeleteView):
    model = Entry
    template_name = 'gn_manager/delete.html'
    success_message = 'Entry was deleted.'
    success_url = reverse_lazy('manager')

    def dispatch(self, request, *args, **kwargs):
        if not Entry.objects.filter(pk=kwargs['pk']).exists():
            return HttpResponse(status=404)
        elif not Entry.objects.filter(user=request.user,pk=kwargs['pk']).exists():
            return HttpResponse(status=403)
        return super().dispatch(request, *args, **kwargs)