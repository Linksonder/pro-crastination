from django.shortcuts import render
from django.template import loader
from django.shortcuts import render
from django.core.files.base import ContentFile
import os
import io
import base64

# Create your views here.
from django.http import HttpResponse
import logging
logger = logging.getLogger(__name__)

import app.controllers.AnalyseController as ac

def index(request):
    context = {
        'msg': 'hello world',
    }
    return render(request, 'index.html', context)

def analyse(request):
    name = upload(request)
    logging.error(name)
    result = ac.analyseDatabase(name)
    context = {
        'result': img(result)
    }
    free(name)
    return render(request, 'analyse.html', context)

def img(plt):
    buffer = io.BytesIO()
    plt.figure.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    graphic = base64.b64encode(image_png)
    graphic = graphic.decode('utf-8')
    return graphic


def upload(request):
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/../..'
    folder = 'databases'
    uploaded_filename = request.FILES['database'].name

    # create the folder if it doesn't exist.
    try:
        os.mkdir(os.path.join(PROJECT_ROOT, folder))
    except:
        pass

    # save the uploaded file inside that folder.
    full_filename = os.path.join(PROJECT_ROOT, folder, uploaded_filename)
    fout = open(full_filename, 'wb+')

    file_content = ContentFile( request.FILES['database'].read() )

    # Iterate through the chunks.
    for chunk in file_content.chunks():
        fout.write(chunk)
    fout.close()

    return full_filename

def free(name):
    os.remove(name)