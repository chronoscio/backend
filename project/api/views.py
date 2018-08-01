from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser

from .models import *
from .serializers import NationSerializer

@csrf_exempt
def nation_list(request):
    """
    List all nations, or create a new nation.
    """
    if request.method == 'GET':
        nations = Nation.objects.all()
        serializer = NationSerializer(nations, many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = NationSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)

@csrf_exempt
def nation_detail(request, pk):
    """
    Retrieve, update or delete a nation.
    """
    try:
        nation = Nation.objects.get(pk=pk)
    except Nation.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = NationSerializer(nation)
        return JsonResponse(serializer.data)

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = NationSerializer(nation, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)

    elif request.method == 'DELETE':
        nation.delete()
        return HttpResponse(status=204)
