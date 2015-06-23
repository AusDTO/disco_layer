from django.shortcuts import render

def index(request):
    return render(request, 'index.html', {})

def about_search(request):
    return render(request, 'intro/search.html', {})

def about_api(request):
    return render(request, 'intro/api.html', {})

def about_for_gov(request):
    return render(request, 'intro/for_gov.html', {})

def about_hacking(request):
    return render(request, 'intro/hacking.html', {})

########
def search(request):
    return render(request, 'search/index.html', {})

def api(request):
    return render(request, 'api/index.html', {})

def for_gov(request):
    return render(request, 'for_gov/index.html', {})
