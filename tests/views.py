import json

from django.http import HttpResponse


def home(request):
    return HttpResponse(b"<html><body>Home</body></html>")


def about(request):
    return HttpResponse(b"<html><body>About</body></html>")


def data_json(request):
    return HttpResponse(
        json.dumps({"ok": True}), content_type="application/json"
    )


def feed(request):
    return HttpResponse(
        json.dumps({"items": []}), content_type="application/json"
    )


def binary(request):
    return HttpResponse(
        b"\x00\x01\x02\x03", content_type="application/octet-stream"
    )


def fails(request):
    return HttpResponse("nope", status=500)
