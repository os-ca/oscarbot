from datetime import datetime, timedelta
import re
def get_eventid(eventid):
    global url,event_id
    event_id = eventid
    tmrw_ = (''.join(re.split('-',str(datetime.strptime(str((datetime.today()+timedelta(days=1)))[:10], "%Y-%m-%d").date()))))
    url = f"https://ubc.perfectmind.com/24063/Clients/BookMe4EventParticipants?eventId={event_id}&occurrenceDate={tmrw_}&&locationId=27a6cd2c-34a1-40f9-822e-cf70b5bca13c&waitListMode=False" 
    return url, event_id