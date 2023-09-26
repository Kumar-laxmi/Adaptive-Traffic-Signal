from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'index.html', {})

def index_temp(request):
    return render(request, 'index_temp.html', {})