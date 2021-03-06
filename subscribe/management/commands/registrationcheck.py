from django.core.management.base import BaseCommand
from django.db.transaction import commit_on_success

from subscribe.models import Registration
import datetime

class Command(BaseCommand):
    
    @commit_on_success
    def handle(self, *args, **options):
        now = datetime.datetime.now()
        days = 7
        seconds = 0
        hourInSeconds = 60*60
        
        # Get all registrations that are not payed, have a trxid and where 
        # check_ttl > 0 to check their payment status.        
        for r in Registration.objects.filter(payed=False).filter(trxid__isnull=False).filter(check_ttl__gt=0):
            isOlderThanSevenDays = now > ( r.registration_date + datetime.timedelta(days, seconds) )
            isCheckedLastHour = False
            if (r.payment_check_dates.count() > 0):
              isCheckedLastHour = now > ( r.payment_check_dates.all().latest('date').date + datetime.timedelta(0, hourInSeconds) )
            
            # only check if the registration is not older than 7 days
            # only check if there has not been a check the last hour
            if (not isOlderThanSevenDays) and (not isCheckedLastHour):
                r.check_payment_status()
