from django.shortcuts import render

def show_main(request):
    context = {
        'kelompok': 'kelompok-e10'
    }

    return render(request, "main.html", context);

def show_about(request):

    return render(request, "about.html");