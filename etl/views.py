from django.shortcuts import render
from django.http import HttpResponse
from django.core.handlers.wsgi import WSGIRequest
from django.core.files.uploadedfile import InMemoryUploadedFile
import boto3
from .forms import UploadFileForm
import random
import string
from simetric.settings import S3_BUCKET
from etl.map_reduce import Map

def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for _ in range(length))
    return result_str


def router(request: WSGIRequest):
    if request.method == 'POST':
        return post_upload(request)
    return get_index(request)


def get_index(request: WSGIRequest):
    return HttpResponse("Metodo get.")


def post_upload(request: WSGIRequest):
    form = UploadFileForm(request.POST, request.FILES)
    if form.is_valid():
        handle_uploaded_file(request.FILES['file'])
        response = HttpResponse('{"success": true}')
        response['content-type'] = 'application/json'
        return response
    else:
        response = '{"success": false,"message": "Petición mal formada"}'
        response = HttpResponse(response, status=400)
        response['content-type'] = 'application/json'
        return response


def handle_uploaded_file(f: InMemoryUploadedFile):
    
    # name = get_random_string(10) + '-' + f.name ""

    name = f.name
    fname = '/tmp/' + name
    mapper = Map()
    mapper.name = name.split('.')[0]

    cont = 0
    with open(fname, 'wb+') as destination:
        while True:
            chunk = f.read(1024)
            if not chunk:
                break
            destination.write(chunk)
            if cont == 0:
                mapper.apply(chunk, True)
            else:
                mapper.apply(chunk)
            cont = cont +1

        destination.close()
        mapper.end()

    s3client = boto3.client('s3')
    s3client.put_object(
        Body=fname,
        Bucket=S3_BUCKET,
        Key='uploads/'+name
    )
