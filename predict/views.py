from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import datetime
import pytz
from django.http import JsonResponse

from django.core.files.storage import default_storage


# Create your views here.


@api_view(['GET'])
def predict_view(request):
    file_path = 'static/text.txt'
    file = default_storage.open(file_path, 'r')
    file_content = file.read()
    file.close()
    return Response(file_content)


@api_view(['POST'])
def predict_post(request):
    file_path = 'static/text.txt'
    file = default_storage.open(file_path, 'r')
    file_content = file.read()
    file.close()
    output_data = request.data
    output_data['file_data'] = file_content
    return JsonResponse({"data": output_data})
