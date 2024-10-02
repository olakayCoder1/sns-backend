from io import BytesIO
import json
import os
import time
import requests
import urllib.parse
from django.conf import settings
from django.shortcuts import redirect
from jwt_auth.models import UserInfo
from db_schema.models import SocialConfig
from rest_framework.response import Response
from requests_oauthlib import OAuth1Session
from django.conf import settings
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required

# VIDEO_URL = 'https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerMeltdowns.mp4'



class TwitterMediaManager:

    def __init__(self, *args,**kwargs):
        pass

 

    def twitter_authorize(self,request,config_id):
        consumer_key = settings.TWITTER_API_KEY
        consumer_secret = settings.TWITTER_API_SECRET

        oauth = OAuth1Session(consumer_key, client_secret=consumer_secret)
        
        request_token_url = "https://api.twitter.com/oauth/request_token?oauth_callback=oob&x_auth_access_type=write"
        
        fetch_response = oauth.fetch_request_token(request_token_url)
        resource_owner_key = fetch_response.get("oauth_token")
        resource_owner_secret = fetch_response.get("oauth_token_secret")

        # Save the tokens temporarily in session for the next step
        request.session['resource_owner_key'] = resource_owner_key
        request.session['resource_owner_secret'] = resource_owner_secret
        request.session['config_id'] = config_id

        # Get authorization URL
        base_authorization_url = "https://api.twitter.com/oauth/authorize"
        authorization_url = oauth.authorization_url(base_authorization_url)

        response = {'redirectUrl': authorization_url}
        return 200, response
    


    def twitter_callback(self, request):
        consumer_key = settings.TWITTER_API_KEY
        consumer_secret = settings.TWITTER_API_SECRET

        # Validate session data
        config_id = request.session.get('config_id')
        if not config_id:
            return Response({'msg': "Missing configuration ID."}, status=400)

        try:
            social_config = SocialConfig.objects.get(id=config_id)
        except SocialConfig.DoesNotExist:
            return Response({'msg': "Invalid configuration ID."}, status=400)

        resource_owner_key = request.session.get('resource_owner_key')
        resource_owner_secret = request.session.get('resource_owner_secret')
        if not resource_owner_key or not resource_owner_secret:
            return Response({'msg': "Missing OAuth credentials."}, status=400)

        verifier = request.GET.get('oauth_verifier')
        if not verifier:
            return Response({'msg': "Missing OAuth verifier."}, status=400)

        # Create OAuth1Session
        oauth = OAuth1Session(
            consumer_key,
            client_secret=consumer_secret,
            resource_owner_key=resource_owner_key,
            resource_owner_secret=resource_owner_secret,
            verifier=verifier,
        )

        # Fetch access tokens
        access_token_url = "https://api.twitter.com/oauth/access_token"
        try:
            oauth_tokens = oauth.fetch_access_token(access_token_url)
        except Exception as e:
            return Response({'msg': f"Error fetching access tokens: {str(e)}"}, status=400)

        access_token = oauth_tokens.get("oauth_token")
        access_token_secret = oauth_tokens.get("oauth_token_secret")

        if not access_token or not access_token_secret:
            return Response({'msg': "Failed to retrieve access tokens."}, status=400)

        # Store tokens in the database
        social_config.twitter_access_token = access_token
        social_config.twitter_access_token_secret = access_token_secret
        social_config.is_active = True
        social_config.verified = True

        try:
            social_config.save()
        except Exception as e:
            return Response({'msg': f"Error saving configuration: {str(e)}"}, status=400)

        # Update user profile
        try:
            user_profile: UserInfo = request.user.user_info
            user_profile.is_twitter = True
            user_profile.save()
        except Exception as e:
            return Response({'msg': f"Error updating user profile: {str(e)}"}, status=400)

        return Response({'msg': "顧客情報が正常に登録されました。"}, status=200)



    def upload_video(self,oauth,file_path):
        # Check if the file_path is a URL
        if file_path.startswith("http://") or file_path.startswith("https://"):

            response = requests.get(file_path, stream=True)
            if response.status_code != 200:
                raise Exception(f"Failed to download video from {file_path}: {response.text}")


            video_content = BytesIO(response.content)
            video_content.seek(0)  # Ensure the stream starts at the beginning
            file_size = len(response.content)
        else:

            if not os.path.exists(file_path):
                raise FileNotFoundError(f"The file {file_path} does not exist.")
            
            file_size = os.path.getsize(file_path)
            
            if file_size == 0:
                raise Exception(f"The file {file_path} is empty (0 bytes).")

            video_content = open(file_path, "rb")


        init_response = oauth.post(
            "https://upload.twitter.com/1.1/media/upload.json",
            data={
                "command": "INIT",
                "media_type": "video/mp4",
                "total_bytes": file_size,
                "media_category": "tweet_video"
            }
        )

        # Check for a successful INIT
        if init_response.status_code not in [200, 202]:
            raise Exception(f"Failed to initialize video upload: {init_response.text}")

        # Extract the media ID
        media_id = init_response.json().get("media_id_string")


        chunk_size = 5 * 1024 * 1024  # 5 MB per chunk
        segment_id = 0
        while True:
            chunk = video_content.read(chunk_size)
            if not chunk:
                break
            append_response = oauth.post(
                "https://upload.twitter.com/1.1/media/upload.json",
                data={
                    "command": "APPEND",
                    "media_id": media_id,
                    "segment_index": segment_id
                },
                files={"media": chunk}
            )
            if append_response.status_code != 204:
                raise Exception(f"Failed to upload chunk {segment_id}: {append_response.text}")
            segment_id += 1

        # Close the file-like object if it was opened
        if isinstance(video_content, BytesIO):
            video_content.close()
        else:
            video_content.close()  # Close the local file

        finalize_response = oauth.post(
            "https://upload.twitter.com/1.1/media/upload.json",
            data={"command": "FINALIZE", "media_id": media_id}
        )

        if finalize_response.status_code != 200:
            raise Exception(f"Failed to finalize video upload: {finalize_response.text}")

        processing_info = finalize_response.json().get("processing_info", None)

        if processing_info:
            state = processing_info["state"]
            check_after_secs = processing_info.get("check_after_secs", 0)
            while state != "succeeded":
                time.sleep(check_after_secs)
                status_response = oauth.get(
                    "https://upload.twitter.com/1.1/media/upload.json",
                    params={"command": "STATUS", "media_id": media_id}
                )
                state = status_response.json()["processing_info"]["state"]
                check_after_secs = status_response.json()["processing_info"].get("check_after_secs", 0)
                if state == "failed":
                    raise Exception(f"Video upload failed: {status_response.text}")

        return media_id
    

    def post_tweet(self,social_config: SocialConfig,video_file,description):
        # Recreate the OAuth session with stored access tokens
        oauth = OAuth1Session(
            settings.TWITTER_API_KEY,
            client_secret=settings.TWITTER_API_SECRET,
            resource_owner_key=social_config.twitter_access_token,
            resource_owner_secret=social_config.twitter_access_token_secret,
        )

        try:
            media_id = self.upload_video(oauth, video_file)
        except Exception as e:
            return {"error": str(e)}

        payload = {
            "text": description,
            "media": {"media_ids": [media_id]}
        }

        # Post the tweet
        response = oauth.post("https://api.twitter.com/2/tweets", json=payload)

        if response.status_code != 201:
            return {"error": response.text}
        return {"msg": "Tweet posted successfully!"}
