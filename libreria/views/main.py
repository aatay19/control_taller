import io
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse

@login_required
def index(request):
    context = {}
    return render(request, 'index.html', context)
