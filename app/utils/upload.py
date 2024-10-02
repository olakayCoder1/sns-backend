from django.conf import settings
import pathlib
import uuid
import os


def upload_evidence(file):
    os.makedirs(os.path.join(settings.MEDIA_ROOT, "evidence"), exist_ok=True)
    gallery_directory = os.path.join(settings.MEDIA_ROOT, 'evidence')
    
    filename = str(uuid.uuid4()) + pathlib.Path(file.name).suffix

    with open(os.path.join(gallery_directory, filename), 'wb') as f:
        for chunk in file.chunks():
            f.write(chunk)

    return filename
