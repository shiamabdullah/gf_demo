from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import datetime
from django.http import JsonResponse
from django.conf import settings
from django.core.files.storage import default_storage
import pandas as pd
import os

# Create your views here.

base_dir = settings.BASE_DIR


@api_view(['GET'])
def predict_view(request):
    file_path = 'static/text.txt'
    file = default_storage.open(file_path, 'r')
    file_content = file.read()
    file.close()
    return Response(file_content)


# @api_view(['POST'])
# def predict_post(request):
#     file_path = 'static/text.txt'
#     file = default_storage.open(file_path, 'r')
#     file_content = file.read()
#     file.close()
#     output_data = request.data
#     output_data['file_data'] = file_content
#     return JsonResponse({"data": output_data})


@api_view(['POST'])
def predict_post(request):
    # loading the models directory
    file_path = 'static/gen_model'
    models = os.listdir(file_path)
    new_keys = {'area': 'total_area_of_chip',
                'frequency': 'achieved_frequency_ghz',
                'vnom': 'vnom',
                'power': 'tp_ff_ext_max_125',
                # 'country': 'beol',
                'city': 'beol'
                }

    # Create a new dictionary with only the keys in new_keys, and with their names mapped to the new names
    new_data = {new_keys.get(k, k): v for k,
                v in request.data.items() if k in new_keys}
    input_data_as_df = pd.DataFrame(new_data, index=[0])
    print(input_data_as_df)
    cols = list(input_data_as_df.columns)

    model_to_load = ""
    for j in range(len(models)):
        model = models[j].split("_to_")
        model_cols = []
        list_of_features = ['achieved_frequency_ghz', 'vnom',
                            'tp_ff_ext_max_125', 'total_area_of_chip', 'beol']
        for k in range(len(list_of_features)):
            if list_of_features[k] in model[0]:
                model_cols.append(list_of_features[k])

        if model_cols == cols:
            model_to_load = models[j]
            return JsonResponse({"output": models[j]})

    return JsonResponse({"data": "hasdsd"})
