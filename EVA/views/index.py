# -*- coding: utf-8 -*-
from django.shortcuts import render


def index_view(request):
    return render(request, 'EVA/index.html')
