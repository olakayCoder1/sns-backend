from datetime import datetime
import json
import os , time
from venv import logger
from django.core.files.storage import default_storage
import uuid
from django.utils import timezone
from utils.socials.twitter import TwitterMediaManager
from rest_framework.serializers import ValidationError
from datetime import datetime, timezone as dt_timezone
from api.v0.customer.member.serializers import CustomersSocialConfigCreateSerializer, PostDispatchPayloadSerializer, SocialConfigListSerializer, SocialConfigUpdateSerializer
from utils.socials.instagram import InstagramMediaManager
from jwt_auth.tasks import backgroud_upload, schedule_for_background_upload
from utils.socials.youtube import YouTubeManager
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import FileResponse
from django.shortcuts import redirect
from django.db.models import *
from django.db import transaction
from tempfile import NamedTemporaryFile
from db_schema.models import *
from db_schema.serializers import *
from utils.permissions import *
from validations.customer import *

# Create your views here.



class CreateCustomersSocialConfigAPI1(APIView):
    permission_classes = [IsCustomer]

    def post(self,request):

        serializer = CustomersSocialConfigCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)


        social_type = serializer.validated_data['ads']
        data=request.data

        # Validate the 'ads' field
        valid_providers = [item for sublist in SocialConfig.AVAILABLE_PROVIDER for item in sublist]
        if social_type not in valid_providers:
            raise ValidationError({'ads': 'The value selected is not a valid choice'})
        

        if social_type == 'YOUTUBE':
            required_fields = ['google_client_id', 'google_client_secret', 'google_project_id']
            missing_fields = [field for field in required_fields if not data.get(field)]
            if missing_fields:
                raise ValidationError({field: f'This field is required when ads is {social_type}' for field in missing_fields})

        elif social_type == 'INSTAGRAM':
            required_fields = ['facebook_client_secret', 'facebook_app_id', 'instagram_business_id']
            missing_fields = [field for field in required_fields if not data.get(field)]
            if missing_fields:
                raise ValidationError({field: f'This field is required when ads is {social_type}' for field in missing_fields})


        social_type = serializer.validated_data['ads']

        if social_type == "YOUTUBE":
            social_config = SocialConfig.objects.create(
                added_by=request.user,
                provider=social_type,
                name=serializer.validated_data['name'],
                youtube_client_id=serializer.validated_data['google_client_id'],
                youtube_client_secret=serializer.validated_data['google_client_secret'],
                youtube_project_id=serializer.validated_data['google_project_id'],
            )
            status_code, response=  YouTubeManager.authenticate_user(request,social_config)
            return Response(response,status=status_code)
        
        elif social_type == 'INSTAGRAM':

            social_config = SocialConfig.objects.create(
                added_by=request.user,
                provider=social_type,
                name=serializer.validated_data['name'],
                instagram_business_id=request.data['instagram_business_id'],
                facebook_app_id=request.data['facebook_app_id'],
                facebook_client_secret=request.data['facebook_client_secret'],
            )

            instagram_manager = InstagramMediaManager()
            status_code, response= instagram_manager.facebook_login(request.data['facebook_app_id'],social_config.id)
            
            return Response(response,status=status_code)

        return Response({"msg": "顧客情報が正常に登録されました。"})



class CreateCustomersSocialConfigAPI(APIView):
    permission_classes = [IsCustomer]

    def post(self, request):
        # Deserialize request data
        serializer = CustomersSocialConfigCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        social_type = serializer.validated_data['ads']
        data = request.data

        # Validate social_type
        valid_providers = [item for sublist in SocialConfig.AVAILABLE_PROVIDER for item in sublist]
        if social_type not in valid_providers:
            raise ValidationError({'ads': '選択された値は有効な選択肢ではありません。'})
        
        

        # Validate required fields based on social_type
        self._validate_required_fields(social_type, data)


        # Check if the user already has this type of credentials
        if SocialConfig.objects.filter(added_by=request.user, provider=social_type, verified = True).exists():
            return Response(
                {"msg": "指定されたタイプの認証情報は既に登録されています。"},
                status=400
            )

        # Create SocialConfig instance
        social_config = self._create_social_config(social_type, serializer.validated_data, request.user)

        # Authenticate user and return response
        if social_type == "YOUTUBE":
            status_code, response = YouTubeManager.authenticate_user(request, social_config)
        elif social_type == 'INSTAGRAM':
            instagram_manager = InstagramMediaManager()
            status_code, response = instagram_manager.facebook_login(data['facebook_app_id'], social_config.id)

        elif social_type == 'TWITTER':
            twitter_manager = TwitterMediaManager()
            status_code, response = twitter_manager.twitter_authorize(request,social_config.id)
        else:
            return Response({"msg": "無効なソーシャルタイプが提供されました"}, status=400)

        return Response(response, status=status_code)

    def _validate_required_fields(self, social_type, data):
        """Validate required fields based on the social_type."""
        if social_type == 'YOUTUBE':
            required_fields = ['google_client_id', 'google_client_secret', 'google_project_id']
        elif social_type == 'INSTAGRAM':
            required_fields = ['facebook_client_secret', 'facebook_app_id', 'instagram_business_id']
        else:
            return

        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            raise ValidationError({field: f'このフィールドは{social_type}の場合に必要です。' for field in missing_fields})

    def _create_social_config(self, social_type, validated_data, user):
        """Create and return a SocialConfig instance based on the social_type."""
        config_params = {
            'added_by': user,
            'provider': social_type,
            'name': validated_data['name']
        }

        if social_type == 'YOUTUBE':
            config_params.update({
                'youtube_client_id': validated_data['google_client_id'],
                'youtube_client_secret': validated_data['google_client_secret'],
                'youtube_project_id': validated_data['google_project_id']
            })
        elif social_type == 'INSTAGRAM':
            config_params.update({
                'instagram_business_id': validated_data['instagram_business_id'],
                'facebook_app_id': validated_data['facebook_app_id'],
                'facebook_client_secret': validated_data['facebook_client_secret']
            })

        return SocialConfig.objects.create(**config_params)



class CreateCustomersSocialConfigCallbackAPI(APIView):
    permission_classes = [IsCustomer]

    def get(self,request):
        state = request.GET.get('state')

        print(request.GET)

        try:
            if state:
                try:
                    extra_params = json.loads(state)
                except:
                    extra_params = eval(state)

                config_id = extra_params.get('configID')
                try:
                    config = SocialConfig.objects.get(id=config_id)
                except:return Response({},status=404)


                if config.provider == "INSTAGRAM":
                    code = request.GET.get('code')
                    instagram_manager = InstagramMediaManager()
                    return instagram_manager.facebook_callback(
                        code=code,
                        social_config=config,
                        request=request
                    )
                
                elif config.provider == "INSTAGRAM":

                    return YouTubeManager.callback_handler(request,config)

            else:

                time.sleep(5)
                # return Response({"msg": "顧客情報が正常に登録されました。"},status=500)
                if request.GET.get('oauth_verifier'):
                    twitter_manager = TwitterMediaManager()
                    return twitter_manager.twitter_callback(request)
            return Response({"msg": "顧客情報が正常に登録されました。"})
        except Exception as e:
            print(e)
            return Response({"msg": "エラーが発生しました。再試行してください。"},status=500)
    


class GetCustomersSocialConfigAPI(APIView):
    permission_classes = [IsCustomer]

    def get(self,request,customer_id):
        try:

            social_configs = SocialConfig.objects.get(id=customer_id)
        except Exception as e:
            print(e)
            return Response({"msg": "顧客情報が正常に登録されました。"},status=404)
        
        serializers = SocialConfigListSerializer(social_configs)

        return Response({"msg": "顧客情報が正常に登録されました。","data":serializers.data})
    


    def delete(self,request,customer_id):
        try:
            social_config = SocialConfig.objects.get(id=customer_id)
        except:return Response({"msg": "顧客情報が正常に登録されました。"},status=404)
        
        


        try:
            user_profile:UserInfo = request.user.user_info
            if social_config.provider == 'YOUTUBE':
                user_profile.is_youtube = False
            elif social_config.provider == 'INSTAGRAM':
                user_profile.is_instagram = False
            user_profile.save()
        except:pass
        social_config.delete()
        return Response({"msg": "顧客情報が正常に登録されました。"})
    

    def patch(self,request,customer_id):
        try:

            social_config = SocialConfig.objects.get(id=customer_id)
        except:return Response({"msg": "顧客情報が正常に登録されました。"},status=404)
        
        serializer = SocialConfigUpdateSerializer(social_config, data=request.data, partial=True)
        
        serializer.is_valid(raise_exception=True)
        serializer.save()
        print(request.data)
        serializers = SocialConfigListSerializer(social_config)
        return Response({"msg": "顧客情報が正常に登録されました。","data":serializers.data})
    


class GetCustomersSocialConfigForRefreshAPI(APIView):
    permission_classes = [IsCustomer]

    def get(self,request,customer_id):
        try:

            social_config = SocialConfig.objects.get(id=customer_id)
        except Exception as e:
            print(e)
            return Response({"msg": "顧客情報が正常に登録されました。"},status=404)
        
        if social_config.provider == "YOUTUBE":
            status_code, response = YouTubeManager.authenticate_user(request, social_config)
        elif social_config.provider == 'INSTAGRAM':
            instagram_manager = InstagramMediaManager()
            status_code, response = instagram_manager.facebook_login(social_config.facebook_app_id, social_config.id)
        else:
            return Response({"msg": "無効なソーシャルタイプが提供されました"}, status=400)
        

        return Response(response, status=status_code)
    


class ListCustomersSocialConfigAPI(APIView):
    permission_classes = [IsCustomer]

    def get(self,request):
        role = get_role(request.user)
        if role == "admin":
            social_configs = SocialConfig.objects.filter().order_by("-created_at")
        elif role == "member":
            social_configs = SocialConfig.objects.filter(added_by=request.user).order_by("-created_at")
        else:
            raise Exception("Forbidden")
        
        
        serializers = SocialConfigListSerializer(social_configs, many=True)

        return Response({"msg": "顧客情報が正常に登録されました。","data":serializers.data})


class DispatchVideoAPI(APIView):
    permission_classes = [IsCustomer]

    def post(self, request):
        serializer = PostDispatchPayloadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # time.sleep(10)

        # return Response({"msg": "顧客情報が正常に登録されました。"}, status=400)

        # File size validation
        videos = request.FILES.getlist('video')
        max_size_mb = 100
        for video in videos:
            if video.size > max_size_mb * 1024 * 1024:
                return Response(
                    {'video': f'File size exceeds {max_size_mb} MB.'},
                    status=400
                )

        # Determine chosen platforms
        choices = [key.upper() for key in ['youtube', 'tiktok', 'instagram','twitter'] if request.data.get(f'is_{key}') == 'true']



        print(choices)
        print(choices)
        print(choices)
        print(choices)
        description = serializer.validated_data['description']
        title = serializer.validated_data['title']
        youtube_title = request.data.get('youtube_title')
        youtube_description = request.data.get('youtube_description')
        tiktok_description = request.data.get('tiktok_description')
        instagram_description = request.data.get('instagram_description')
        twitter_description = request.data.get('twitter_description')

        status_code = 200

        try:
            processing_id = str(uuid.uuid4())
            user_id = request.user.id

            with transaction.atomic():
                video_objs = [
                    ScheduleVideo.objects.create(
                        file=video,
                        added_by=request.user,
                        processing_id=processing_id,
                        title=title,
                        youtube_description=youtube_description,
                        tiktok_description=tiktok_description,
                        instagram_description=instagram_description,
                        twitter_description=twitter_description,
                        youtube_title=youtube_title,
                        socials=choices,
                        description=description
                    ) for video in videos
                ]

                if request.data.get("instance_dispatch") == "true":
                    schedule_for_background_upload.delay(
                        title,
                        description,
                        user_id,
                        processing_id,
                        choices
                    )
                else:
                    task_datetime = serializer.validated_data['task_datetime']

                    # Ensure task_datetime is timezone-aware and in 'Africa/Lagos' timezone
                    task_datetime_aware = timezone.make_aware(task_datetime, timezone.get_current_timezone())
                    
                    task_datetime_utc = task_datetime_aware.astimezone(dt_timezone.utc)

                    schedule_for_background_upload.apply_async(
                        args=[title, description, user_id, processing_id, choices],
                        eta=task_datetime_utc
                    )

        except Exception as e:
            logger.error(f"An error occurred: {e}")
            return Response({"msg": "リクエストの処理中にエラーが発生しました"}, status=500)

        return Response({"msg": "顧客情報が正常に登録されました。"}, status=status_code)




class GetCustomersAPI(APIView):
    permission_classes = [IsCustomer]
    
    def get(self, request):
        keyword = request.GET.get('keyword', '')
        order_by = request.GET.get('order_by', 'id')
        manager = int(request.GET.get('manager', 0))
        status = int(request.GET.get('status', 0))
        property = int(request.GET.get('property', 0))
        page = int(request.GET.get('page', 1))
        pageSize = int(request.GET.get('pageSize', 10))

        customer_ids = request.GET.getlist('customer_ids[]', [])
        expanded = request.GET.get('expanded', "")
        

        try:
            m_data = Customer.objects.all()

            role = get_role(request.user)

            if len(customer_ids) > 0:
                m_data = m_data.filter(id__in=customer_ids)
            
            if role == "admin":
                if manager != 0:
                    m_data = m_data.filter(manager=User.objects.filter(id=manager).first())
            elif role == "member":
                m_data = m_data.filter(manager=request.user)
            else:
                raise Exception("Forbidden")
                
            if Status.objects.filter(id=status).exists():
                m_data = m_data.filter(status=Status.objects.filter(id=status).first())

            if Property.objects.filter(id=property).exists():
                m_data = m_data.filter(property=Property.objects.filter(id=property).first())

            if keyword != "":
                m_data = m_data.filter(Q(manager__user_info__name__contains=keyword) | Q(ads__contains=keyword) | Q(name__contains=keyword) | Q(phone__contains=keyword) | Q(email__contains=keyword) | Q(phone_2__contains=keyword) | Q(email_2__contains=keyword))

            m_data = m_data.order_by(order_by)
            
            if expanded == "False":
                serializer = CustomerNameSerializer(m_data, many=True)

                return Response({
                    "data": serializer.data,
                    "total": m_data.count()
                })
            else:
                serializer = CustomerSerializer(m_data[pageSize * (page - 1):pageSize * page], many=True)

                return Response({
                    "data": serializer.data,
                    "total": m_data.count()
                })
            
        except Exception as e:
            print(str(e))
            return Response(str(e), status=500)
        

class CreateCustomerAPI(APIView):
    permission_classes = [IsCustomer]
    
    def post(self, request):
        
        try:
            errors, status, clean_data = validate_create_customer(request)
            
            if status != 200:
                return Response({"errors": errors}, status=status)
            
            with transaction.atomic():
                customer = Customer.objects.create(
                    name=clean_data["last_name"] + " " + clean_data["first_name"],
                    last_name=clean_data["last_name"],
                    first_name=clean_data["first_name"],
                    email=clean_data["email"],
                    phone=clean_data["phone"],
                    email_2=clean_data["email_2"],
                    phone_2=clean_data["phone_2"],
                    ads=clean_data["ads"],
                    deposit_date=clean_data["deposit_date"],
                    contract_start_date=clean_data["contract_start_date"],
                    contract_days=clean_data["contract_days"],
                    status=Status.objects.filter(id=clean_data["status"]).first(),
                    property=Property.objects.filter(id=clean_data["property"]).first(),
                    system_provided=clean_data["system_provided"],
                    manager=request.user
                )

                return Response({
                    "msg": "顧客情報が正常に登録されました。",
                    "data": CustomerSerializer(customer).data
                })
        except Exception as e:
            print(str(e))
            return Response({"msg": str(e)}, status=400)
        


class CreateBatchCustomerAPI(APIView):
    permission_classes = [IsCustomer]
    
    def post(self, request):
        data = dict(request.data)

        try:
            res = []
            customers = data.get('data', [])

            for customer in customers:
                name = customer.get('name', '')
                if len(name.split(' ')) == 2:
                    last_name = name.split(' ')[0]
                    first_name = name.split(' ')[1]
                else:
                    last_name = name
                    first_name = ''
                email = customer.get('email', '')
                phone = customer.get('phone', '')
                email_2 = customer.get('email_2', '')
                phone_2 = customer.get('phone_2', '')
                ads = customer.get('ads', '')
                deposit_date = customer.get('deposit_date', None)
                contract_start_date = customer.get('contract_start_date', None)

                try:
                    contract_days = int(customer.get('contract_days', 0))
                except:
                    contract_days = 0
                    
                status = customer.get('status', '')
                property = customer.get('property', '')
                system_provided = customer.get('system_provided', "NG")

                try:
                    role = get_role(request.user)
                    if role == "member":
                        manager= request.user
                    elif role == "admin":
                        manager = User.objects.filter(user_info__name=customer.get('manager', '')).first()
                        if manager is None:
                            manager= request.user
                    
                    if name == "" or email == "" or phone == "" or Customer.objects.filter(email=email).exists():
                        raise Exception("Invalid Data")

                    with transaction.atomic():
                        # get last name and first name from name

                        m_customer = Customer.objects.create(
                            name = name,
                            last_name = last_name,
                            first_name = first_name,
                            email = email,
                            phone = phone,
                            email_2 = email_2,
                            phone_2 = phone_2,
                            ads = ads,
                            deposit_date = deposit_date,
                            contract_start_date = contract_start_date,
                            contract_days = contract_days,
                            status = Status.objects.filter(name=status).first(),
                            property = Property.objects.filter(name=property).first(),
                            system_provided = True if system_provided == "OK" else False,
                            manager = manager
                        )

                        res.append({
                            "data": customer,
                            "status": 200
                        })
                except Exception as e:
                    print(str(e))
                    res.append({
                        "data": customer,
                        "status": 400
                    })


            return Response(res)
        except Exception as e:
            print(str(e))
            return Response({"msg": str(e)}, status=400)
        

class UpdateCustomerAPI(APIView):
    permission_classes = [IsCustomer]

    def get(self, request, customer_id):
        keyword = request.GET.get('keyword', '')
        order_by = request.GET.get('order_by', 'id')
        manager = int(request.GET.get('manager', 0))
        status = int(request.GET.get('status', 0))
        property = int(request.GET.get('property', 0))
        page = int(request.GET.get('page', 1))
        pageSize = int(request.GET.get('pageSize', 10))

        try:
            m_customer = Customer.objects.filter(id=customer_id)

            role = get_role(request.user)
            if role == "member":
                m_customer = m_customer.filter(manager=request.user)
            elif role == "admin":
                pass
            else:
                raise Exception("Forbidden")

            m_customer = m_customer.first()
            
            if m_customer is None:
                raise Exception("データが見つかりません。")
            
            serializer = CustomerFlatSerializer(m_customer)

            
            m_data = Customer.objects.all()

            role = get_role(request.user)
            
            if role == "admin":
                if manager != 0:
                    m_data = m_data.filter(manager=User.objects.filter(id=manager).first())
            elif role == "member":
                m_data = m_data.filter(manager=request.user)
            else:
                raise Exception("Forbidden")
                
            if Status.objects.filter(id=status).exists():
                m_data = m_data.filter(status=Status.objects.filter(id=status).first())

            if Property.objects.filter(id=property).exists():
                m_data = m_data.filter(property=Property.objects.filter(id=property).first())

            if keyword != "":
                m_data = m_data.filter(Q(manager__user_info__name__contains=keyword) | Q(ads__contains=keyword) | Q(name__contains=keyword) | Q(phone__contains=keyword) | Q(email__contains=keyword) | Q(phone_2__contains=keyword) | Q(email_2__contains=keyword))

            m_data = m_data.order_by(order_by)
            
            prev = 0
            next = 0

            for i in range(m_data.count()):
                if m_data[i].id == m_customer.id:
                    if i > 0:
                        prev = m_data[i-1].id
                    if i < m_data.count()-1:
                        next = m_data[i+1].id

            return Response({
                "data": serializer.data,
                "prev": prev,
                "next": next
            })
        except Exception as e:
            print(str(e))
            return Response(str(e), status=500)
        

    def patch(self, request, customer_id):
        
        try:
            errors, status, clean_data = validate_update_customer(request, customer_id)
            
            if status != 200:
                return Response({"errors": errors}, status=status)
            
            with transaction.atomic():
                customer = Customer.objects.get(id=customer_id)
                
                customer.name = clean_data["last_name"] + " " + clean_data["first_name"]
                customer.last_name = clean_data["last_name"]
                customer.first_name = clean_data["first_name"]
                customer.email = clean_data["email"]
                customer.phone = clean_data["phone"]
                customer.email_2 = clean_data["email_2"]
                customer.phone_2 = clean_data["phone_2"]
                customer.ads = clean_data["ads"]
                customer.deposit_date = clean_data["deposit_date"]
                customer.contract_start_date = clean_data["contract_start_date"]
                customer.contract_days = clean_data["contract_days"]
                customer.status = Status.objects.filter(id=clean_data["status"]).first()
                customer.property = Property.objects.filter(id=clean_data["property"]).first()
                customer.system_provided = clean_data["system_provided"]
                customer.save()

                return Response({
                    "msg": "顧客情報が正常に更新されました。"
                })
        except Exception as e:
            print(str(e))
            return Response({"msg": str(e)}, status=400)
        
    
    def delete(self, request, customer_id):
        try:
            errors, status, clean_data = validate_delete_customer(request, customer_id)
            
            if status != 200:
                return Response({"errors": errors}, status=status)
            
            customer = Customer.objects.get(id=customer_id)
            customer.delete()

            return Response({
                "msg": "顧客情報が正常に削除されました。"
            })
        except Exception as e:
            print(str(e))
            return Response({"msg": str(e)}, status=400)
        

class DownloadCustomerAPI(APIView):
    permission_classes = [IsCustomer]
    
    def get(self, request):
        try:
            customers = Customer.objects.all()

            role = get_role(request.user)
            if role == "member":
                customers = customers.filter(manager=request.user)
            
            import os
            import xlsxwriter
            from uuid import uuid4
            import datetime
            
            if not os.path.exists(f"storage/customers"):
                os.makedirs(f"storage/customers")

            path = f"storage/customers/{uuid4()}.xlsx"

            workbook = xlsxwriter.Workbook(path)
            worksheet = workbook.add_worksheet()

            font_format = workbook.add_format({'font_name': 'Yu Mincho'})
            row = 0
            worksheet.write(row, 0, "広告媒体", font_format)
            worksheet.write(row, 1, "氏名", font_format)
            worksheet.write(row, 2, "メールアドレス", font_format)
            worksheet.write(row, 3, "電話番号", font_format)
            worksheet.write(row, 4, "メールアドレス2", font_format)
            worksheet.write(row, 5, "電話番号2", font_format)
            if role == "admin":
                worksheet.write(row, 6, "担当者", font_format)
                worksheet.write(row, 7, "入金日", font_format)
                worksheet.write(row, 8, "契約開始日", font_format)
                worksheet.write(row, 9, "契約日数", font_format)
                worksheet.write(row, 10, "属性", font_format)
                worksheet.write(row, 11, "ステータス", font_format)
                worksheet.write(row, 12, "システム提供", font_format)
            else:
                worksheet.write(row, 6, "入金日", font_format)
                worksheet.write(row, 7, "契約開始日", font_format)
                worksheet.write(row, 8, "契約日数", font_format)
                worksheet.write(row, 9, "属性", font_format)
                worksheet.write(row, 10, "ステータス", font_format)
                worksheet.write(row, 11, "システム提供", font_format)

            row += 1

            for customer in customers:
                worksheet.write(row, 0, customer.ads, font_format)
                worksheet.write(row, 1, customer.name, font_format)
                worksheet.write(row, 2, customer.email, font_format)
                worksheet.write(row, 3, customer.phone, font_format)
                worksheet.write(row, 4, customer.email_2, font_format)
                worksheet.write(row, 5, customer.phone_2, font_format)
                if role == "admin":
                    worksheet.write(row, 6, customer.manager.user_info.name, font_format)
                    worksheet.write(row, 7, datetime.datetime.strftime(customer.deposit_date, "%Y-%m-%d") if customer.deposit_date else "", font_format)
                    worksheet.write(row, 8, datetime.datetime.strftime(customer.contract_start_date, "%Y-%m-%d") if customer.contract_start_date else "", font_format)
                    worksheet.write(row, 9, customer.contract_days, font_format)
                    worksheet.write(row, 10, customer.property.name if customer.property else "", font_format)
                    worksheet.write(row, 11, customer.status.name if customer.status else "", font_format)
                    worksheet.write(row, 12, "OK" if customer.system_provided else "NG", font_format)
                else:
                    worksheet.write(row, 6, datetime.datetime.strftime(customer.deposit_date, "%Y-%m-%d") if customer.deposit_date else "", font_format)
                    worksheet.write(row, 7, datetime.datetime.strftime(customer.contract_start_date, "%Y-%m-%d") if customer.contract_start_date else "", font_format)
                    worksheet.write(row, 8, customer.contract_days, font_format)
                    worksheet.write(row, 9, customer.property.name if customer.property else "", font_format)
                    worksheet.write(row, 10, customer.status.name if customer.status else "", font_format)
                    worksheet.write(row, 11, "OK" if customer.system_provided else "NG", font_format)
                
                row += 1
            workbook.close()

            return FileResponse(open(path, 'rb'), status=200)
        except Exception as e:
            print(str(e))
            return Response(str(e), status=500)
        



