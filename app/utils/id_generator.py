import uuid
import datetime

from .models import *

def generator(request):
    current_datetime = datetime.datetime.now().strftime("%Y%m%d%H%M%S")


    return f"{request.user.id}_{current_datetime}_{uuid.uuid1()}"