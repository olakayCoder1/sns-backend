import json
import time
import requests
import urllib.parse
from django.conf import settings
from django.shortcuts import redirect
from jwt_auth.models import UserInfo
from db_schema.models import SocialConfig
from rest_framework.response import Response


# VIDEO_URL = 'https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerMeltdowns.mp4'



class InstagramMediaManager:
    def __init__(self, instagram_business_account_id=None, access_token=None):
        """
        Initializes the InstagramMediaManager with necessary credentials.

        Args:
            instagram_business_account_id (str, optional): The Instagram Business Account ID.
            access_token (str, optional): Access token for authenticating API requests.
        """
        self.access_token = access_token
        self.instagram_business_account_id = instagram_business_account_id
        self.base_url = 'https://graph.facebook.com/v20.0'  # Base URL for Facebook Graph API

    def facebook_login(self, facebook_app_id, config_id):
        """
        Generates a Facebook OAuth authorization URL for user login.

        Args:
            facebook_app_id (str): The Facebook App ID.
            config_id (str): Identifier for the social media configuration.

        Returns:
            tuple: HTTP status code and a dictionary containing the authorization URL.
        """
        state = urllib.parse.urlencode({'configID': config_id})
        state_data = {'configID': config_id}
        state = json.dumps(state_data)
        # Define the scopes required for the Instagram API
        scope = ("publish_video,pages_show_list,instagram_basic,instagram_manage_comments,"
                 "instagram_manage_insights,instagram_content_publish,instagram_manage_messages,"
                 "pages_read_engagement,pages_manage_posts,instagram_branded_content_brand,"
                 "instagram_branded_content_creator,instagram_branded_content_ads_brand,public_profile")
        # Construct the authorization URL
        auth_url = (
            f"https://www.facebook.com/v20.0/dialog/oauth?"
            f"client_id={facebook_app_id}&"
            f"redirect_uri={settings.FACEBOOK_REDIRECT_URI}&scope="
            f"{scope}&"
            f"state={state}&" 
            f"response_type=code"
        )
        response = {'redirectUrl': auth_url}
        print(auth_url)
        # Return the authorization URL for redirecting the user
        return 200, response

    def facebook_callback(self, code, social_config: SocialConfig,**kwargs):
        """
        Handles the Facebook OAuth callback, exchanges the authorization code for an access token, 
        and verifies permissions.

        Args:
            code (str): Authorization code received from Facebook.
            social_config (SocialConfig): Social media configuration object.

        Returns:
            Response: HTTP response with status and message.
        """
        request = kwargs.get('request')
        if not code:
            return 400, 'No code provided'

        # Construct the token exchange URL
        token_url = (
            f"{self.base_url}/oauth/access_token?"
            f"client_id={social_config.facebook_app_id}&"
            f"redirect_uri={settings.FACEBOOK_REDIRECT_URI}&"
            f"client_secret={social_config.facebook_client_secret}&"
            f"code={code}"
        )

        response = requests.get(token_url)
        data = response.json()

        if response.status_code == 200:
            access_token = data.get('access_token')
            # Check the granted permissions
            permissions_url = (
                f"https://graph.facebook.com/me/permissions?"
                f"access_token={access_token}"
            )
            permissions_response = requests.get(permissions_url)

            if permissions_response.status_code == 200:
                permissions_data = permissions_response.json()
                granted_permissions = [
                    perm['permission'] for perm in permissions_data['data'] if perm['status'] == 'granted'
                ]

                # Verify required permissions
                expected_permissions = ["instagram_content_publish", "publish_video"]
                for perm in expected_permissions:
                    if perm not in granted_permissions:
                        social_config.delete()
                        return Response({'msg': f"Permission '{perm}' not granted."}, status=400)

            # Save the access token and update social configuration
            social_config.facebook_access_token = access_token
            social_config.verified = True
            social_config.save()
            # get the user and update the user social record
            try:
                user_profile:UserInfo = request.user.user_info
                user_profile.is_youtube = True
                user_profile.save()
            except:pass
            return Response({'msg': "顧客情報が正常に登録されました。"}, status=200)
        else:
            return Response({'msg': f"Error: {data.get('error', {}).get('message', 'Unknown error')}"}, status=400)

    def create_media_container(self, video_url, caption):
        """
        Creates a media container for uploading a video to Instagram.

        Args:
            video_url (str): URL of the video to be uploaded.
            caption (str): Caption for the video.

        Returns:
            dict: JSON response from Instagram API containing the media container information.
        """
        url = f'{self.base_url}/{self.instagram_business_account_id}/media'
        params = {
            'video_url': video_url,  # For videos
            'caption': caption,
            'media_type': 'REELS',  # Type of media being uploaded
            'access_token': self.access_token
        }
        response = requests.post(url, params=params)
        print(response.url)
        return response.json()

    def container_status(self, container_id):
        """
        Checks the status of the media container.

        Args:
            container_id (str): ID of the media container to check.

        Returns:
            dict: JSON response from Instagram API containing the status of the media container.
        """
        url = f'{self.base_url}/{container_id}'
        params = {
            'fields': 'status_code',
            'access_token': self.access_token
        }
        response = requests.get(url, params=params)

        # Print the HTTP status code and raw response content
        print(f"HTTP Status Code: {response.status_code}")
        print(f"Response Content: {response.text}")

        # Parse and handle JSON response
        json_response = response.json()

        if response.status_code == 200:
            return json_response
        else:
            # Print detailed error information
            error_message = json_response.get('error', {}).get('message', 'No error message provided')
            error_type = json_response.get('error', {}).get('type', 'Unknown error type')
            error_code = json_response.get('error', {}).get('code', 'Unknown error code')

            print(f"Error Message: {error_message}")
            print(f"Error Type: {error_type}")
            print(f"Error Code: {error_code}")

            return json_response

    def publish_media_container(self, container_id):
        """
        Publishes the media container once the status is 'FINISHED'.

        Args:
            container_id (str): ID of the media container to publish.

        Returns:
            dict: JSON response from Instagram API with the result of the publish operation.
        """
        response = self.container_status(container_id)
        print(f"Container status ::: {response}")

        if response.get('status_code') == 'FINISHED':
            url = f'{self.base_url}/{self.instagram_business_account_id}/media_publish'
            params = {
                'creation_id': container_id,
                'access_token': self.access_token
            }
            response = requests.post(url, params=params)
            return response.json()
        elif response.get('status_code') == 'IN_PROGRESS':
            time.sleep(20)
            return self.publish_media_container(container_id)
        elif response.get('status_code') == 'ERROR':
            return {"error": "18057806071688227"}  # Return a specific error code
        else:
            return {'error': 'Container not ready for publishing.'}

    def handle_video_upload(self, video_url, caption):
        """
        Main method to handle the entire video upload process, from creating a media container 
        to publishing it.

        Args:
            video_url (str): URL of the video to be uploaded.
            caption (str): Caption for the video.

        Returns:
            dict: JSON response with the result of the video upload operation.
        """

        # Step 1: Create a media container
        response = self.create_media_container(video_url, caption)
        if 'id' in response:
            container_id = response['id']
            print(f"Media container created with ID: {container_id}")

            # Step 2: Wait for some time and check status
            time.sleep(20)

            # Step 3: Publish the media container
            publish_response = self.publish_media_container(container_id)
            return publish_response
        else:
            return {'error': 'Error creating media container', 'details': response}
