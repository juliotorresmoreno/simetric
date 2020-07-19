from django import forms
from django.db import models


class UploadFileForm(forms.Form):
    uploadfile = models.FileField()
