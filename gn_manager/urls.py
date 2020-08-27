from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('',views.manager,name='manager'),
    path('create/',login_required(views.EntryCreateView.as_view()),name='create'),
    path('edit/<int:pk>',login_required(views.EntryEditView.as_view()),name='edit'),
    path('delete/<int:pk>',login_required(views.EntryDeleteView.as_view()),name='delete')
]