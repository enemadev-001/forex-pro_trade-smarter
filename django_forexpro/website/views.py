from django.shortcuts import render

def home(request):
    return render(request, 'website/index.html')

def loading(request):
    return render(request, 'website/loading.html')
