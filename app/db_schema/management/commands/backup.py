from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.core import management
from django.db import transaction
from django.db.models import *


class Command(BaseCommand):
    help = "Closes the specified poll for voting"


    def handle(self, *args, **options):

        from datetime import datetime

        today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
        management.call_command(f"dbbackup", f"-o cms_wavemaster_db_backup_{today}.sql")
        management.call_command(f"mediabackup", f"-o cms_wavemaster_media_backup_{today}.tar")
