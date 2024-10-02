from django.contrib.auth.middleware import AuthenticationMiddleware
from django.http import JsonResponse

from db_schema.models import *

class NotificationMiddleware(AuthenticationMiddleware):
    def __init__(self, get_response):
        self.get_response = get_response
        self.unread_msg_cnt = 0

    def __call__(self, request):
        response = super().__call__(request) 
        self.checkMessagesIncoming(request)
        
        # Modify the content of the response to include custom data
        response.content = self.add_custom_data(response.content)

        return response

    
    # Check if client IP is allowed
    def process_request(self, request):
       # If IP is allowed we don't do anything
        return None
    
    def process_response(self, request, response):
        self.unread_msg_cnt = 0
        return response
    

    def checkMessagesIncoming(self, request):
        try:
            if not request.user.is_authenticated:
                self.unread_msg_cnt = 0
                return
            
            permission = request.user.permission
            
            if permission == "member":
                m_applications = JobApplication.objects.filter(user=request.user)
                m_messages = JobMessage.objects.filter(application__in=m_applications, is_read=False, sender_type="employer")
                self.unread_msg_cnt = m_messages.count()
        except:
            self.unread_msg_cnt = 0
            return 
        
    def add_custom_data(self, original_content):
        # Parse the original content as JSON
        content_dict = json.loads(original_content.decode('utf-8'))

        # Add custom data to the dictionary
        content_dict['unread_msg'] = {
            "total": self.unread_msg_cnt,
        }

        # Convert the dictionary back to JSON and return as bytes
        return json.dumps(content_dict).encode('utf-8')