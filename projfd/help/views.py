from django.shortcuts import render

def api(request):
    return render(request, "help/api.html", {})
