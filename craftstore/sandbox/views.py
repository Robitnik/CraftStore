from django.shortcuts import render

def sand_box(request):
    return render(request, "sandbox.html")