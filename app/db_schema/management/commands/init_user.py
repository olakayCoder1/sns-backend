from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.hashers import make_password
from django.db import transaction
from db_schema.models import *
import json



class Command(BaseCommand):
    help = "Closes the specified poll for voting"


    def handle(self, *args, **options):
        self.init_user()

    def init_user(self):
        
        with open('db_schema/management/commands/data/user.json', 'r', encoding="utf-8") as f:
            data = json.load(f)

            for user in data:
                with transaction.atomic():
                    user_info = UserInfo.objects.create(
                        name = user["last_name"] + " " + user["first_name"],
                        last_name = user["last_name"],
                        first_name = user["first_name"],
                        name_furi = user["last_name_furi"] + " " + user["first_name_furi"],
                        last_name_furi = user["last_name_furi"],
                        first_name_furi = user["first_name_furi"],
                        phone = user["phone"],
                        role = Role.objects.get(role_id=user["role_id"])
                    )

                    user = User.objects.create(
                        email = user["email"],
                        user_info = user_info,
                        password = make_password(user["password"]),
                    )
