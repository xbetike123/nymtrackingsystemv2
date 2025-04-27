from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

@login_required
def dummy_view(request):
    return HttpResponse("<h1>This page will be built soon...</h1>")
