from django.shortcuts import render

def sand_box(request):
    return render(request, "sandbox.html")


def ws_sand_box(request):
    return render(request, "test/ws.html")


def ws_chat_sand_box(request, slug):
    return render(request, "test/chat_ws.html", context={"chat_slug": slug})
