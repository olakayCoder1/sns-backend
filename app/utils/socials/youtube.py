import time 
import json 
from io import BytesIO 
from jwt_auth.models import UserInfo
from googleapiclient.http import MediaIoBaseUpload  
from googleapiclient.errors import HttpError 
from urllib.parse import urlencode  
from django.http import HttpResponseRedirect  
from db_schema.models import SocialConfig 
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload 
from google_auth_oauthlib.flow import Flow 
from google.oauth2.credentials import Credentials 
import google.auth.transport.requests 
from rest_framework.response import Response 
import os

# Set environment variable to allow OAuth library to use HTTP (insecure) for local development
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

class YouTubeManager:
    # OAuth 2.0 client configuration
    CLIENT_SECRETS_FILE = {
        "web": {
            "client_id": "",  # Placeholder for client ID
            "project_id": "",  # Placeholder for project ID
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",  # Authorization URI
            "token_uri": "https://oauth2.googleapis.com/token",  # Token exchange URI
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",  # URL for OAuth provider certificates
            "client_secret": "",  # Placeholder for client secret
            "redirect_uris": ["http://localhost:3000", "http://localhost:8000", "http://127.0.0.1:8000"],  # Allowed redirect URIs
            "javascript_origins": ["http://localhost:3000", "http://127.0.0.1:8000"]  # Allowed JavaScript origins
        }
    }

    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']  # Scope for uploading videos to YouTube
    API_SERVICE_NAME = 'youtube'  # YouTube API service name
    API_VERSION = 'v3'  # YouTube API version
    REDIRECT_URI = 'http://localhost:3000/snsaccounts/create'  # URI to redirect after OAuth authentication

    @staticmethod
    def authenticate_user(request, config: SocialConfig, extra_params: dict = None):
        """
        Initiates the OAuth 2.0 authorization process for the user.

        Args:
            request: The HTTP request object.
            config (SocialConfig): Social media configuration object.
            extra_params (dict, optional): Additional parameters to include in the authorization URL.

        Returns:
            tuple: HTTP status code and a dictionary containing the redirect URL.
        """
        # Update client secrets with configuration details
        CLIENT_SECRETS_FILE = YouTubeManager.CLIENT_SECRETS_FILE
        CLIENT_SECRETS_FILE['web']['client_id'] = config.youtube_client_id
        CLIENT_SECRETS_FILE['web']['client_secret'] = config.youtube_client_secret
        CLIENT_SECRETS_FILE['web']['project_id'] = config.youtube_project_id

        extra_params = {"configID": config.id}
        # Save the configuration to the database
        config.youtube_credentials = CLIENT_SECRETS_FILE
        config.save()
        print(CLIENT_SECRETS_FILE)

        # Configure the OAuth flow
        flow = Flow.from_client_config(CLIENT_SECRETS_FILE, scopes=YouTubeManager.SCOPES)
        flow.redirect_uri = YouTubeManager.REDIRECT_URI

        # Create and encode the state parameter
        state_data = {'configID': config.id}
        state = json.dumps(state_data)
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent',
            state=state
        )

        # Append extra parameters to the authorization URL
        if extra_params:
            query_params = urlencode(extra_params)
            authorization_url = f"{authorization_url}&{query_params}"

        # Save the state in the session
        request.session['state'] = state

        # Return the authorization URL for redirecting the user
        response = {'redirectUrl': authorization_url}
        return 200, response

    @staticmethod
    def callback_handler(request, config: SocialConfig):
        """
        Handles the OAuth 2.0 callback and exchanges the authorization code for tokens.

        Args:
            request: The HTTP request object.
            config (SocialConfig): Social media configuration object.

        Returns:
            Response: HTTP response with status and message.
        """
        try:
            # Retrieve the saved credentials
            CLIENT_SECRETS_FILE = None
            user_tokens = config
            CLIENT_SECRETS_FILE = user_tokens.youtube_credentials

            if not CLIENT_SECRETS_FILE:
                return Response({'message': 'YouTube credentials are missing.'}, status=400)

            # Configure the OAuth flow
            flow = Flow.from_client_config(CLIENT_SECRETS_FILE, scopes=YouTubeManager.SCOPES)
            flow.redirect_uri = YouTubeManager.REDIRECT_URI

            # Fetch tokens using the authorization response
            authorization_response = request.build_absolute_uri()
            flow.fetch_token(authorization_response=authorization_response)

            credentials = flow.credentials
            
            # Save credentials data
            youtube_credentials_data = {
                'token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': credentials.scopes
            }
            print(youtube_credentials_data)

            # Update the user's configuration with new tokens
            user_tokens.youtube_token = credentials.token
            user_tokens.youtube_refresh_token = credentials.refresh_token
            user_tokens.youtube_credentials = CLIENT_SECRETS_FILE
            user_tokens.scopes = credentials.scopes
            user_tokens.youtube_credentials_data = youtube_credentials_data
            user_tokens.verified = True
            user_tokens.save()


            # get the user and update the user social record
            try:
                user_profile:UserInfo = request.user.user_info
                user_profile.is_youtube = True
                user_profile.save()
            except:pass


            return Response({'msg': "顧客情報が正常に登録されました。"}, status=200)

        except ValueError as ve:
            # Handle invalid credentials or authorization response
            return Response({'msg': f'ValueError: {str(ve)}'}, status=400)

        except Exception as e:
            # Handle unexpected errors
            return Response({'msg': f'An unexpected error occurred: {str(e)}'}, status=500)

    @staticmethod
    def notify_user(error_message: str):
        """
        Notify the user about an error.

        Args:
            error_message (str): The error message to be sent to the user.
        """
        # TODO: Implement logic to notify the user, such as sending an email or a notification.
        print(f'Notify user: {error_message}')

    @staticmethod
    def upload_video(social_config: SocialConfig, video_file, title, description, payload: dict = {}) -> tuple:
        """
        Uploads a video to YouTube.

        Args:
            social_config (SocialConfig): Social media configuration object.
            video_file: The video file to upload.
            title (str): The title of the video.
            description (str): The description of the video.
            payload (dict, optional): Additional data to be included in the request.

        Returns:
            tuple: HTTP status code, video ID, and video URL.
        """
        user_tokens = social_config
        print("******" * 20)
        credentials_data = user_tokens.youtube_credentials_data
        if not credentials_data:
            return 401, 'User not authenticated', 'User not authenticated'

        # Create credentials object and refresh if expired
        credentials = Credentials(**credentials_data)
        if credentials.expired and credentials.refresh_token:
            request_refresh = google.auth.transport.requests.Request()
            credentials.refresh(request_refresh)

        # Build the YouTube service object
        youtube = build(YouTubeManager.API_SERVICE_NAME, YouTubeManager.API_VERSION, credentials=credentials)
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'categoryId': '22',  # Category ID for 'People & Blogs'
            },
            'status': {
                'privacyStatus': 'public'  # Set video visibility to public
            }
        }
        try:
            # Convert video file to BytesIO stream if it's not already
            if hasattr(video_file, 'read'):
                video_file_stream = BytesIO(video_file.read())
            else:
                video_file_stream = BytesIO(video_file)

            # Create media upload object
            media_body = MediaIoBaseUpload(video_file_stream, mimetype='video/mp4')

            # Insert video into YouTube
            request = youtube.videos().insert(
                part="snippet,status",
                body=body,
                media_body=media_body
            )
            response = request.execute()
            video_id = response['id']
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            return 200, video_id, video_url

        except HttpError as e:
            # Handle HTTP errors from the API
            error_content = e.error_details or {}
            if e.resp.status == 403:
                # Notify user if YouTube quota is exceeded
                YouTubeManager.notify_user('YouTube quota exceeded. Please check your API usage.')
                return 400, 'Quota exceeded', 'Quota exceeded'
            elif e.resp.status == 400:
                # Notify user of a bad request
                print(f'Bad request: {e}')
                YouTubeManager.notify_user('Bad request: Check the request details.')
                return 400, 'Bad request', 'Bad request'
            else:
                # Notify user of an unexpected error
                print(f'An error occurred: {e}')
                return 400, str(e), str(e)
