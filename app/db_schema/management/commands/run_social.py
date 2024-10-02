from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.hashers import make_password
from django.db import transaction
from utils.socials.instagram import InstagramMediaManager
from db_schema.models import *
import json




class Command(BaseCommand):
    help = "Closes the specified poll for voting"


    def handle(self, *args, **options):
        

        video = ScheduleVideo.objects.filter().last()
        print(video.file.url)

        config = SocialConfig.objects.filter().last()

        print(config.provider)
        print(config.instagram_business_id)
        print(config.facebook_access_token)

        instagram_manager = InstagramMediaManager(instagram_business_account_id=config.instagram_business_id,access_token=config.facebook_access_token)
        res = instagram_manager.handle_video_upload(video_url=video.file.url,caption='Media container created with ID')

        print(res)


