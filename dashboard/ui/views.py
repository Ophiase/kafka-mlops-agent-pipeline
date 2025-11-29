from django.http import HttpRequest, HttpResponse, HttpResponse
from django.shortcuts import render


def dashboard(request: HttpRequest) -> HttpResponse:
    data = {
        "fetcher": {
            "number_fetched": 0,
            "number_sent_to_kafka": 0,
        },
        "processor": {
            "in_process": 0,
            "number_sent_to_kafka": 0,
        }
    }
    return render(request, "dashboard.html", data)
