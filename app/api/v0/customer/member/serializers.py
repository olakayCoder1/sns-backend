from rest_framework import serializers
import json
from datetime import datetime, date, time
from db_schema.models import *
from django_mailbox.models import Message, MessageAttachment


class MessageAttachmentSerializer(serializers.ModelSerializer):
    document = serializers.SerializerMethodField()

    class Meta:
        model = MessageAttachment
        fields = ["id", "document"]

    def get_document(self, obj):
        
        return {
            "name": obj.document.file.name,
            "url": obj.document.file.url,
            "content_type": obj.document.file.content_type
        }


class MessageSerializer(serializers.ModelSerializer):
    attachments = MessageAttachmentSerializer(many=True)
    body = serializers.SerializerMethodField()
    sender = serializers.SerializerMethodField()
    receiver = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = "__all__"

    def get_body(self, obj):

        return obj.html
    
    
    def get_sender(self, obj):

        return obj.from_address
    
    
    def get_receiver(self, obj):

        return obj.to_address
    



class CustomersSocialConfigCreateSerializer(serializers.Serializer):
    ads = serializers.CharField(required=True)
    name = serializers.CharField(required=True)

    google_client_id = serializers.CharField(required=False, allow_blank=True)
    google_client_secret = serializers.CharField(required=False, allow_blank=True)
    google_project_id = serializers.CharField(required=False, allow_blank=True)

    facebook_client_secret = serializers.CharField(required=False, allow_blank=True)
    facebook_app_id = serializers.CharField(required=False, allow_blank=True)
    instagram_business_id = serializers.CharField(required=False, allow_blank=True)

    def validate_(self, data):

        print(data)
        print(data)
        print(data)
        if data.get('ads') not in  [item for sublist in SocialConfig.AVAILABLE_PROVIDER for item in sublist]:
            raise serializers.ValidationError({'ads': 'The value selected is not a valid choice'}) 

        if data.get('ads') == 'YOUTUBE' :
            if not data.get('google_client_id'):
                raise serializers.ValidationError({'google_client_id': 'This field is required when ads is YOUTUBE'})
            
            if not data.get('google_client_secret'):
                raise serializers.ValidationError({'google_client_secret': 'This field is required when ads is YOUTUBE'})
            
            if not data.get('google_project_id'):
                raise serializers.ValidationError({'google_project_id': 'This field is required when ads is YOUTUBE'})
        
        if data.get('ads') == 'INSTAGRAM' :
            if not data.get('facebook_client_secret'):
                raise serializers.ValidationError({'facebook_client_secret': 'This field is required when ads is INSTAGRAM'})
            
            if not data.get('facebook_app_id'):
                raise serializers.ValidationError({'facebook_app_id': 'This field is required when ads is INSTAGRAM'})
            
            if not data.get('instagram_business_id'):
                raise serializers.ValidationError({'instagram_business_id': 'This field is required when ads is INSTAGRAM'})
        

        
            
        return data
    


class SocialConfigListSerializer(serializers.ModelSerializer):
    added_by = serializers.SerializerMethodField()
    class Meta:
        model = SocialConfig
        fields = [
            'id',
            'added_by',
            'name',
            'provider',
            # 'youtube_token',
            'youtube_client_id',
            'youtube_client_secret',
            'youtube_project_id',
            'facebook_client_secret',
            'facebook_app_id',
            'instagram_business_id',
            'is_active',
            'created_at'
        ]
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        youtube_client_id = representation.get('youtube_client_id')
        youtube_client_secret = representation.get('youtube_client_secret')
        youtube_project_id = representation.get('youtube_project_id')
        
        if youtube_client_id:
            if len(youtube_client_id) > 10:
                representation['youtube_client_id'] = (
                    youtube_client_id[:6] + '*' * (10) + youtube_client_id[-4:]
                )

        if youtube_client_secret:
            if len(youtube_client_secret) > 10:
                representation['youtube_client_secret'] = (
                    youtube_client_secret[:6] + '*' * (10) + youtube_client_secret[-4:]
                )

        if youtube_project_id:
            if len(youtube_project_id) > 10:
                representation['youtube_project_id'] = (
                    youtube_project_id[:6] + '*' * (10) + youtube_project_id[-4:]
                )
        
        
        facebook_client_secret = representation.get('facebook_client_secret')
        facebook_app_id = representation.get('facebook_app_id')
        instagram_business_id = representation.get('instagram_business_id')

        if facebook_client_secret:
            if len(facebook_client_secret) > 10:
                representation['facebook_client_secret'] = (
                    facebook_client_secret[:6] + '*' * (10) + facebook_client_secret[-4:]
                )

        if facebook_app_id:
            if len(facebook_app_id) > 10:
                representation['facebook_app_id'] = (
                    facebook_app_id[:6] + '*' * (10) + facebook_app_id[-4:]
                )

        if instagram_business_id:
            if len(instagram_business_id) > 10:
                representation['instagram_business_id'] = (
                    instagram_business_id[:6] + '*' * (10) + instagram_business_id[-4:]
                )

        
        return representation


    
    def get_added_by(self, obj):
        if obj.added_by:
            user = obj.added_by
            return {
                'id': user.id,
                'first_name': user.user_info.first_name,
                'last_name': user.user_info.last_name,
                'phone': user.user_info.phone,
                'email': user.email
            }
        return None
    


class SocialConfigUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = SocialConfig
        fields = ['is_active']

class PostDispatchPayloadSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(max_length=1000)
    youtube_title = serializers.CharField(max_length=255)
    youtube_description = serializers.CharField(max_length=1000)
    tiktok_description = serializers.CharField(max_length=1000)
    instagram_description = serializers.CharField(max_length=1000)
    twitter_description = serializers.CharField(max_length=350)
    is_youtube = serializers.BooleanField()
    is_tiktok = serializers.BooleanField()
    is_instagram = serializers.BooleanField()
    instance_dispatch = serializers.BooleanField()
    date = serializers.DateField(required=False)
    time = serializers.TimeField(required=False)
    # video = serializers.ListField(
    #     child=serializers.FileField()
    # )

    video = serializers.ListField(
        child=serializers.FileField(max_length=1000000, allow_empty_file=False, use_url=False),
        write_only=True
    )

    def validate(self, data):
        instance_dispatch = data.get('instance_dispatch')

        if not instance_dispatch:
            # If instance_dispatch is False, date and time are required
            task_date = data.get('date')
            task_time = data.get('time')
            
            if task_date is None:
                raise serializers.ValidationError({'date': 'This field is required when instance_dispatch is False.'})
            
            if task_time is None:
                raise serializers.ValidationError({'time': 'This field is required when instance_dispatch is False.'})
            
            # Combine date and time into a datetime object
            task_datetime = datetime.combine(task_date, task_time)
            print(task_datetime)
            print(task_datetime.weekday())
            print(task_datetime.date().month)
            print(datetime.now())
            # Check if the scheduled datetime is in the future
            if task_datetime <= datetime.now():
                if task_date >= datetime.now().date():
                    raise serializers.ValidationError({'time': 'The scheduled time must be in the future'})
                raise serializers.ValidationError({'date': 'The scheduled date and time must be in the future'})
                # raise serializers.ValidationError("The scheduled time must be in the future.")
            data['task_datetime'] = task_datetime
        
        # if is_youtube:
        #     youtube_title:str = data.get('youtube_title','')
            
        #     if len(youtube_title.strip()) < 0:
        #         raise serializers.ValidationError({'date': 'This field is required when instance_dispatch is False.'})


        return data
    
    
