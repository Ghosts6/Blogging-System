from django.shortcuts import redirect

def home_view(request):
    return redirect('http://127.0.0.1:8001/docs')