from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import datetime
from django.http import JsonResponse
from django.conf import settings
from django.core.files.storage import default_storage
import pandas as pd
import os
import tensorflow as tf
import keras
import pickle
import sklearn

# Create your views here.

base_dir = settings.BASE_DIR

file_path = 'static/models/'
gen_model_path = file_path+"gen_model/"


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
def predict_post_prev(request):
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


@api_view(['POST'])
def predict_post(request):
    # loading the models directory
    models = os.listdir(file_path+"gen_model")
    new_keys = {'area': 'total_area_of_chip',
                'frequency': 'achieved_frequency_ghz',
                'vnom': 'vnom',
                'power': 'tp_ff_ext_max_125',
                # 'country': 'beol',
                'city': 'beol'
                }

    ##### GET THE MODEL TO BE LOADED ACCORDING TO THE INPUTS ############
    new_data = {new_keys.get(k, k): v for k,
                v in request.data.items() if k in new_keys}
    input_data_as_df = pd.DataFrame(new_data, index=[0])
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

    #### LOAD THE MODEL AND  PREDICT  ###################################
    x1 = keras.models.load_model(gen_model_path+model_to_load)
    # print(x1.summary())
    # print(file_path + "encoder.pkl")
    with open(file_path + "encoder.pkl", 'rb') as file:
        my_oe = pickle.load(file)

    df_cols = list(input_data_as_df.columns)

    # x1_test = pd.read_csv(file_path + 'output.csv', usecols=df_cols)
    # could use this asd well no need to add as csv
    x1_test = input_data_as_df
    # print("x1_test", x1_test)
    # print("df", input_data_as_df)
    x1_test['beol'] = my_oe.transform(x1_test[['beol']])
    x1_pred = x1.predict(x1_test)
    # print("x1_pred  "+str(list(x1_pred)))

    ## SPLIT THE PREDICTED ARRAY AND SHOW THE RESULT ###################################################
    units_dict = {'achieved_frequency_ghz': 'Ghz', 'vnom': 'V',
                  'tp_ff_ext_max_125': 'mW', 'total_area_of_chip': 'um^2'}
    model_used = model_to_load
    model_used = model_used.split("_to_")[1]
    model_used_cols = []

    for l in range(len(list_of_features)):
        if list_of_features[l] in model_used:
            model_used = model_used.replace(
                list_of_features[l], list_of_features[l]+"TT")
            model_used = model_used.replace("TT_", "TT").strip("")
            model_used_cols = model_used.split("TT")
    model_used_cols.remove("")

    output = {}
    for m in range(len(model_used_cols)):
        value = str(x1_pred[m]).replace(
            "array[[", "").replace("]], dtype=float32)", "")
        value = value.replace("[[", "").replace("]]", "")

        if model_used_cols[m] == "total_area_of_chip":
            value = float(value)*10000

        output[model_used_cols[m]] = str(
            value)+" "+units_dict[model_used_cols[m]]

    print(output)
    # arr = [{'column_name': k, 'value': v} for k, v in output.items()]

    return JsonResponse({"result": output})
