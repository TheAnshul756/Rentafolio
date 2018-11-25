from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from functools import reduce
# Create your views here.
def index(request):
    
    return render(request,'home/index.html')
