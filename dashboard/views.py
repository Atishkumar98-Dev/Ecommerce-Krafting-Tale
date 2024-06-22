from django.shortcuts import render

# Create your views here.
def dash_index(request):
    context = {}
    return render(request, 'dashboard/index.html', context)