
from django.db.models import *
from db_schema.models import *



def validate_memo(request):
    data = dict(request.data)
    content = data.get("content", "")



    try:
        errors = {}
        
        if content == "":
            errors["content"] = "メモを入力してください。"

        status = 422 if len(errors) > 0 else 200
        clean_data = {
            "content": content
        }

        return errors, status, clean_data
        
    except Exception as e:
        print(str(e))
        
        return {}, 500, {}
    