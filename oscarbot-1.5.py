import requests, json, csv, ctypes, queue, threading, asyncio, platform, sys, re, subprocess
from datetime import datetime
from modules import timer, get_eventid
try:
    from bs4 import BeautifulSoup as bs 
    from colorama import init, Fore 
except ImportError:
    print("Import Error: Installing Dependencies")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'colorama'])
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'bs4'])

'''
Build 0.1.5

Change Log

- Under Cart Hold Timed Event
    - removed the extra GET Request to parse payload values
    - after one test run, the script reads it as element is None.
      however, spots were taken so it means the payload values were indeed 
      correct but the redirect returns None.

- ctype dynamic counters
    - added -1 for carted and failed for cart holding

- added another GET request after successful cart

- added a finally statement to end queue'd tasks

- changed Profile(s) to Thread(s)

- added Cart Mode 2 with a GET Request right after Timed Sleep Event

- notes
    - seems like after a couple POST request, the failed statement is shown
    - maybe the repeated payload values returns "existing member trying to sign up 
      when the POST request intervals are too early

'''

# init stuff
version= str(json.load(open("./data/bot_data.json","r"))['version'])
launcher = str(json.load(open("./data/bot_data.json","r"))['launcher'])
init(convert=True) if platform.system() == "Windows" else init()
ctypes.windll.kernel32.SetConsoleTitleW(f"OSCAR BOT {version} | {launcher}")

def inits():
    global use_proxies,wh_,eventid,threads,delay
    with open("./data/settings.json", "r") as settings:
        data = json.loads(settings.read())
        wh_ = data['webhook']
        threads = data['threads']
        use_proxies = data['use_proxies']
        delay = data['delay']

    global queue_
    queue_ = queue.Queue(maxsize=threads)

    global sleeping, carted, failed, detected,success
    sleeping,carted,failed,detected,success = 0,0,0,0,0

cyan = "\033[96m"
lightblue = "\033[94m"
orange = "\033[33m"

class Logger:
    @staticmethod
    def timestamp():
        return str(datetime.now())[11:-3]
    @staticmethod
    def normal(message):
        print(f"{cyan}[{Logger.timestamp()}] {message}")
    @staticmethod
    def other(message):
        print(f"{orange}[{Logger.timestamp()}] {message}")
    @staticmethod
    def error(message):
        print(f"{Fore.RED}[{Logger.timestamp()}] {message}")
    @staticmethod
    def success(message):
        print(f"{Fore.GREEN}[{Logger.timestamp()}] {message}") 
# constants
login = 'https://portal.recreation.ubc.ca/index.php?r=public%2Findex'
form = "https://ubc.perfectmind.com/24063/Menu/BookMe4RegistrationForms/FillForms"
extras = "https://ubc.perfectmind.com/24063/Clients/BookMe4Extras/Extras"
store = "https://ubc.perfectmind.com/24063/Clients/BookMe4Cart/RedirectToStore"

def get_profiles(n):
    global username,password,user_sig,cc_num,cc_ccv,cc_strt,cc_city,cc_zip,cc_month,cc_year,cc_name,count
    version= str(json.load(open("./data/bot_data.json","r"))['version'])
    new_list = []
    with open("./data/profiles.csv",'r',newline='',encoding="utf-8-sig") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            new_list.extend([[row["username"],row['password'],row['signature'],row['number'],row['ccv'],\
                row['street'],row['city'],row['zip'],row['month'],row['year'],row['fullname']]])
        username,password,user_sig,cc_num,cc_ccv,cc_strt,cc_city,cc_zip,cc_month,cc_year,cc_name = \
            new_list[n][0],new_list[n][1],new_list[n][2],new_list[n][3],new_list[n][4],new_list[n][5],\
            new_list[n][6],new_list[n][7],new_list[n][8],new_list[n][9],new_list[n][10]
        ctypes.windll.kernel32.SetConsoleTitleW(f"OSCAR BOT {version} | {launcher} | Thread(s): {threads}")

def profile_count():
    # counts the number of profiles in the CSV file and returns an int
    global profiles
    with open("./data/profiles.csv",'r',newline='',encoding="utf-8-sig") as csvfile:
        reader = csv.DictReader(csvfile)
        profiles = int(len(list(reader))-1)
        return profiles

def wh(method,checkout,username):
    # webhook
    if method  == "cart_hold":

        data = {
                    "username" : "UBC MY BITCH"
                }
        data["embeds"] = [
                {
                    "title" : f"Cart Hold {checkout}",
                    "timestamp": f"{datetime.utcnow()}",
                    "footer": {
                        "icon_url": "https://cdn.discordapp.com/attachments/854247964612493342/854494516269809664/1WlC-_yW_400x400.jpg",
                        "text": f"oscar bot {version}"
                    },
                    "fields": [
                        {
                            "name": "Event ID",
                            "value": f"{get_eventid.event_id}",
                            "inline": False
                        },
                        {
                            "name": "User",
                            "value": f"{username}",
                            "inline": False
                        }
                                
                    ]
                    
                }
            ]
    elif method  == "test_wh":
        data = {
                    "username" : "UBC MY BITCH"
                }
        data["embeds"] = [
                {
                    "title" : f"Test {checkout}",
                    "timestamp": f"{datetime.utcnow()}",
                    "footer": {
                        "icon_url": "https://cdn.discordapp.com/attachments/854247964612493342/854494516269809664/1WlC-_yW_400x400.jpg",
                        "text": f"oscar bot {version}"
                    }
                }           
            ]
    try:
        result = requests.post(wh_, json = data)   
        result.raise_for_status()   
    except requests.exceptions.HTTPError as e:
        pass
    else:
        pass       

# No GET Request after sleep is done
class CartHold():
    def __init__(self,username,password):
        self.username,self.password = username,password
        queue_.put(self)
        ctypes.windll.kernel32.SetConsoleTitleW(f"OSCAR BOT {version} | {launcher} | Thread(s): {threads} | Delay: {delay} | Sleeping: {sleeping} | Carted: {carted} | Failed: {failed}")
        threading.Thread(target=self.run).start()
    def run(self):
        asyncio.run(self.login_())

    async def login_(self):
        global sleeping, carted, failed
        # header
        headers = {
                'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                }

        # request session
        s = requests.Session()
        # login thru get request
        Logger.normal(f"[{self.username}] Logging In")
        r = s.get(login)   
        soup = bs(r.text,'lxml')
        #csrf token fetch
        try:
            csrf_token = soup.select_one('meta[name="csrf-token"]')['content']
        except AttributeError:
            Logger.error(f"[{self.username}] Error Fetching CSRF Token")
        # Cookie Fetch
        cookies = r.cookies
        # Login Payload
        data = {
            "CredentialForm[email]" : f"{self.username}",
            "CredentialForm[password_curr]" : f"{self.password}",
            "_csrf":f"{csrf_token}",
            "btn_login" : "Login",  
        }
        # POST Login Payload
        try:
            # POST Login URL
            r = s.post(login, cookies=cookies, data=data, headers=headers)
            soup = bs(r.text,'lxml')
            # Finding "Client Element" to see if the Login was successful
            try:
                element = soup.find("h1", {"id" : "online-page-header"})
            except AttributeError:
                Logger.error(f"[{self.username}] Error Fetching Header: Login Issue")

            if element.text == "Client":
                Logger.success(f"[{self.username}] Successfully Logged In [{r.status_code}]")
                ctypes.windll.kernel32.SetConsoleTitleW(f"OSCAR BOT {version} | {launcher} | Thread(s): {threads} | Delay: {delay} | Sleeping: {sleeping} | Carted: {carted} | Failed: {failed}")
                # clientname data used for payload value
                clientname = (soup.find("span",class_="client-name")).text
                Logger.normal(f"[{self.username}] Fetching Payload Data")

                # GET request for the Event Booking Page
                r = s.get(get_eventid.url)
                soup = bs(r.text,'lxml')
                # Important Values for payload
                try:
                    eventid2 = (soup.select_one('input[name="EventId"]')["value"])
                    token = soup.select_one('input[name="__RequestVerificationToken"]')['value']
                    priceid = soup.find(id='ParticipantsFamily_FamilyMembers_0__PriceTypeId')['value']
                    widgetid = soup.find(id='EventInfo_WidgetId')['value']
                    regformid = soup.find(id='EventInfo_RegFormId')['value']
                    calendarid = soup.find(id='EventInfo_CalendarId')['value']
                    programid = soup.find(id='EventInfo_ProgramId')['value']
                    date = soup.find(id="EventInfo_OccurrenceDate")['value']
                    contactid = soup.find(id='ParticipantsFamily_ReferralContactId')['value']
                    facilityid = soup.find(id='EventInfo_FacilityId')['value']
                    parentid = soup.find(id='EventInfo_ParentEventId')['value']
                    locationid = soup.find(id="EventInfo_LocationId")['value']
                except AttributeError:
                    Logger.error(f"[{self.username}] Error Fetching Payload Data")
                # Payload Dict
                data = [
                    ('__RequestVerificationToken', f'{token}'),
                    ('EventInfo.WidgetId', f'{widgetid}'),
                    ('EventInfo.RegFormId', f'{regformid}'),
                    ('EventInfo.CalendarId', f'{calendarid}'),
                    ('EventInfo.ProgramId', f'{programid}'),
                    ('EventInfo.ServiceDurationId', ''),
                    ('EventInfo.LocationId', f'{locationid}'),
                    ('EventInfo.Instructor.Id', ''),
                    ('EventInfo.AppointmentStartDateTimeTicks', '0'),
                    ('EventInfo.OccurrenceDate', f'{date}'),
                    ('ParticipantsFamily.ReferralContactId', f'{contactid}'),
                    ('EventInfo.FacilityId', f'{facilityid}'),
                    ('EventInfo.IgnoreEventCapacity', 'False'),
                    ('EventInfo.ParentEventId', f'{parentid}'),
                    ('LandingPageBackUrl', ''),
                    ('SkipRegistrationForm', 'False'),
                    ('WaitListMode', 'False'),
                    ('AmendmentMode', 'False'),
                    ('AmendmentInitiatorId', ''),
                    ('ParticipantsFamily.EventId', f'{eventid2}'),
                    ('ParticipantsFamily.FamilyMembers[0].MemberId', f'{contactid}'),
                    ('ParticipantsFamily.FamilyMembers[0].AccountId', ''),
                    ('ParticipantsFamily.FamilyMembers[0].FullNameSimple', f'{clientname}'),
                    ('ParticipantsFamily.FamilyMembers[0].FamilyMembership', 'You'),
                    ('ParticipantsFamily.FamilyMembers[0].Photo', ''),
                    ('ParticipantsFamily.FamilyMembers[0].PriceTypeId', f'{priceid}'),
                    ('ParticipantsFamily.FamilyMembers[0].IsParticipating', 'true'),
                    ('ParticipantsFamily.FamilyMembers[0].IsParticipating', 'false'),
                    ('ParticipantsFamily.FamilyMembers[0].AttendanceStatus', ''),
                ]
               
                if timed_event == "y":
                    # timed event: sleeps tasks
                    Logger.other(f"[{self.username}] Sleeping for: {timer.timer(user_time)} second(s)...")
                    sleeping+=1
                    ctypes.windll.kernel32.SetConsoleTitleW(f"OSCAR BOT {version} | {launcher} | Thread(s): {threads} | Delay: {delay} | Sleeping: {sleeping} | Carted: {carted} | Failed: {failed}")
                    await asyncio.sleep(timer.timer(user_time))
                    sleeping-=1
                    ctypes.windll.kernel32.SetConsoleTitleW(f"OSCAR BOT {version} | {launcher} | Thread(s): {threads} | Delay: {delay} | Sleeping: {sleeping} | Carted: {carted} | Failed: {failed}")
                    # Timed Event: ATC process
                    while True:
                        Logger.normal(f"[{self.username}] ATC...")
                        # POST Fill Form
                        r=s.post(form, headers=headers, cookies=cookies, data=data)
                        soup = bs(r.text,'lxml')

                        # This element will determine whether or not session had ATC'd
                        element = soup.find("h2", {"id" : "bm-form-header"})

                        # if element is not found, retry [3 Attempts before terminating]
                        if element is None:
                            failed+=1
                            ctypes.windll.kernel32.SetConsoleTitleW(f"OSCAR BOT {version} | {launcher} | Thread(s): {threads} | Delay: {delay} | Sleeping: {sleeping} | Carted: {carted} | Failed: {failed}")
                            retry=0
                            while retry < 3:
                                Logger.error(f'[{self.username}] Error: Full / Not Opened! Retrying [{retry}]...')
                                wh("cart_hold","Error",self.username)
                                Logger.other(f"[{self.username}] Sleeping... [{delay}]")
                                await asyncio.sleep(int(delay))
                                Logger.normal(f"[{self.username}] Refreshing...")
                                r=s.post(form, headers=headers, cookies=cookies, data=data)
                                retry+=1
                            else:
                                Logger.error(f'[{self.username}] Error: Full / Not Opened! Terminating [{retry}]')
                                return False

                        # successfully carted lesgo
                        elif element.text == "DROP-IN - ADULT - OPEN GYM":
                            carted+=1
                            ctypes.windll.kernel32.SetConsoleTitleW(f"OSCAR BOT {version} | {launcher} | Thread(s): {threads} | Delay: {delay} | Sleeping: {sleeping} | Carted: {carted} | Failed: {failed}")
                            Logger.success(f"[{self.username}] Successfully Carted! [{r.status_code}]")
                            wh("cart_hold","Success",self.username)
                        Logger.other(f"[{self.username}] Sleeping... [{delay}]")
                        await asyncio.sleep(int(delay)) 
                        # GET request for the Event Booking Page
                        r = s.get(get_eventid.url)
                        soup = bs(r.text,'lxml')
                        # Important Values for payload
                        try:
                            eventid2 = (soup.select_one('input[name="EventId"]')["value"])
                            token = soup.select_one('input[name="__RequestVerificationToken"]')['value']
                            priceid = soup.find(id='ParticipantsFamily_FamilyMembers_0__PriceTypeId')['value']
                            widgetid = soup.find(id='EventInfo_WidgetId')['value']
                            regformid = soup.find(id='EventInfo_RegFormId')['value']
                            calendarid = soup.find(id='EventInfo_CalendarId')['value']
                            programid = soup.find(id='EventInfo_ProgramId')['value']
                            date = soup.find(id="EventInfo_OccurrenceDate")['value']
                            contactid = soup.find(id='ParticipantsFamily_ReferralContactId')['value']
                            facilityid = soup.find(id='EventInfo_FacilityId')['value']
                            parentid = soup.find(id='EventInfo_ParentEventId')['value']
                            locationid = soup.find(id="EventInfo_LocationId")['value']
                        except AttributeError:
                            Logger.error(f"[{self.username}] Error Fetching Payload Data")
                        # Payload Dict
                        data = [
                            ('__RequestVerificationToken', f'{token}'),
                            ('EventInfo.WidgetId', f'{widgetid}'),
                            ('EventInfo.RegFormId', f'{regformid}'),
                            ('EventInfo.CalendarId', f'{calendarid}'),
                            ('EventInfo.ProgramId', f'{programid}'),
                            ('EventInfo.ServiceDurationId', ''),
                            ('EventInfo.LocationId', f'{locationid}'),
                            ('EventInfo.Instructor.Id', ''),
                            ('EventInfo.AppointmentStartDateTimeTicks', '0'),
                            ('EventInfo.OccurrenceDate', f'{date}'),
                            ('ParticipantsFamily.ReferralContactId', f'{contactid}'),
                            ('EventInfo.FacilityId', f'{facilityid}'),
                            ('EventInfo.IgnoreEventCapacity', 'False'),
                            ('EventInfo.ParentEventId', f'{parentid}'),
                            ('LandingPageBackUrl', ''),
                            ('SkipRegistrationForm', 'False'),
                            ('WaitListMode', 'False'),
                            ('AmendmentMode', 'False'),
                            ('AmendmentInitiatorId', ''),
                            ('ParticipantsFamily.EventId', f'{eventid2}'),
                            ('ParticipantsFamily.FamilyMembers[0].MemberId', f'{contactid}'),
                            ('ParticipantsFamily.FamilyMembers[0].AccountId', ''),
                            ('ParticipantsFamily.FamilyMembers[0].FullNameSimple', f'{clientname}'),
                            ('ParticipantsFamily.FamilyMembers[0].FamilyMembership', 'You'),
                            ('ParticipantsFamily.FamilyMembers[0].Photo', ''),
                            ('ParticipantsFamily.FamilyMembers[0].PriceTypeId', f'{priceid}'),
                            ('ParticipantsFamily.FamilyMembers[0].IsParticipating', 'true'),
                            ('ParticipantsFamily.FamilyMembers[0].IsParticipating', 'false'),
                            ('ParticipantsFamily.FamilyMembers[0].AttendanceStatus', ''),
                        ] 
                        carted-=1
                
                elif timed_event == "n":
                    # non timed event
                    while True:
                        Logger.normal(f"[{self.username}] ATC...")
                        # POST request on FillForm URL
                        r=s.post(form, headers=headers, cookies=cookies, data=data)
                        soup = bs(r.text,'lxml')
                        # Check to see if successfully carted
                        element = soup.find("h2", {"id" : "bm-form-header"})
                        if element is None:
                            failed+=1
                            ctypes.windll.kernel32.SetConsoleTitleW(f"OSCAR BOT {version} | {launcher} | Thread(s): {threads} | Delay: {delay} | Sleeping: {sleeping} | Carted: {carted} | Failed: {failed}")
                            retry=0
                            while retry < 3:
                                Logger.error(f'[{self.username}] Error: Full / Not Opened! Retrying [{retry}]...')
                                wh("cart_hold","Error",self.username)
                                Logger.other(f"[{self.username}] Sleeping... [{delay}]")
                                await asyncio.sleep(int(delay))
                                Logger.normal(f"[{self.username}] Refreshing...")
                                r=s.post(form, headers=headers, cookies=cookies, data=data)
                                retry+=1
                            else:
                                Logger.error(f'[{self.username}] Error: Full / Not Opened! Terminating [{retry}]')
                                return False
                        
                        if element.text == "DROP-IN - ADULT - OPEN GYM":
                            carted+=1
                            ctypes.windll.kernel32.SetConsoleTitleW(f"OSCAR BOT {version} | {launcher} | Thread(s): {threads} | Delay: {delay} | Sleeping: {sleeping} | Carted: {carted} | Failed: {failed}")
                            Logger.success(f"[{self.username}] Successfully Carted! [{r.status_code}]")
                            wh("cart_hold","Success",self.username)

                        Logger.other(f"[{self.username}] Sleeping... [{delay}]")
                        await asyncio.sleep(int(delay))  
                        # GET request for the Event Booking Page
                        r = s.get(get_eventid.url)
                        soup = bs(r.text,'lxml')
                        # Important Values for payload
                        try:
                            eventid2 = (soup.select_one('input[name="EventId"]')["value"])
                            token = soup.select_one('input[name="__RequestVerificationToken"]')['value']
                            priceid = soup.find(id='ParticipantsFamily_FamilyMembers_0__PriceTypeId')['value']
                            widgetid = soup.find(id='EventInfo_WidgetId')['value']
                            regformid = soup.find(id='EventInfo_RegFormId')['value']
                            calendarid = soup.find(id='EventInfo_CalendarId')['value']
                            programid = soup.find(id='EventInfo_ProgramId')['value']
                            date = soup.find(id="EventInfo_OccurrenceDate")['value']
                            contactid = soup.find(id='ParticipantsFamily_ReferralContactId')['value']
                            facilityid = soup.find(id='EventInfo_FacilityId')['value']
                            parentid = soup.find(id='EventInfo_ParentEventId')['value']
                            locationid = soup.find(id="EventInfo_LocationId")['value']
                        except AttributeError:
                            Logger.error(f"[{self.username}] Error Fetching Payload Data")
                        # Payload Dict
                        data = [
                            ('__RequestVerificationToken', f'{token}'),
                            ('EventInfo.WidgetId', f'{widgetid}'),
                            ('EventInfo.RegFormId', f'{regformid}'),
                            ('EventInfo.CalendarId', f'{calendarid}'),
                            ('EventInfo.ProgramId', f'{programid}'),
                            ('EventInfo.ServiceDurationId', ''),
                            ('EventInfo.LocationId', f'{locationid}'),
                            ('EventInfo.Instructor.Id', ''),
                            ('EventInfo.AppointmentStartDateTimeTicks', '0'),
                            ('EventInfo.OccurrenceDate', f'{date}'),
                            ('ParticipantsFamily.ReferralContactId', f'{contactid}'),
                            ('EventInfo.FacilityId', f'{facilityid}'),
                            ('EventInfo.IgnoreEventCapacity', 'False'),
                            ('EventInfo.ParentEventId', f'{parentid}'),
                            ('LandingPageBackUrl', ''),
                            ('SkipRegistrationForm', 'False'),
                            ('WaitListMode', 'False'),
                            ('AmendmentMode', 'False'),
                            ('AmendmentInitiatorId', ''),
                            ('ParticipantsFamily.EventId', f'{eventid2}'),
                            ('ParticipantsFamily.FamilyMembers[0].MemberId', f'{contactid}'),
                            ('ParticipantsFamily.FamilyMembers[0].AccountId', ''),
                            ('ParticipantsFamily.FamilyMembers[0].FullNameSimple', f'{clientname}'),
                            ('ParticipantsFamily.FamilyMembers[0].FamilyMembership', 'You'),
                            ('ParticipantsFamily.FamilyMembers[0].Photo', ''),
                            ('ParticipantsFamily.FamilyMembers[0].PriceTypeId', f'{priceid}'),
                            ('ParticipantsFamily.FamilyMembers[0].IsParticipating', 'true'),
                            ('ParticipantsFamily.FamilyMembers[0].IsParticipating', 'false'),
                            ('ParticipantsFamily.FamilyMembers[0].AttendanceStatus', ''),
                        ] 
                        carted-=1
            else:
                Logger.error(f"[{self.username}] Login Error")

        except Exception as e:
            Logger.error(f"[{self.username}] {e}")

        finally:
            await asyncio.sleep(1.5)
            # Removes item from our queue
            queue_.get()
            queue_.task_done()
            ctypes.windll.kernel32.SetConsoleTitleW(f"OSCAR BOT {version} | {launcher} | Thread(s): {threads} | Delay: {delay} | Sleeping: {sleeping} | Carted: {carted} | Failed: {failed}")

# Has another GET Request right after sleep is done
class CartHold2():
    def __init__(self,username,password):
        self.username,self.password = username,password
        queue_.put(self)
        ctypes.windll.kernel32.SetConsoleTitleW(f"OSCAR BOT {version} | {launcher} | Thread(s): {threads} | Delay: {delay} | Sleeping: {sleeping} | Carted: {carted} | Failed: {failed}")
        threading.Thread(target=self.run).start()
    def run(self):
        asyncio.run(self.login_())

    async def login_(self):
        global sleeping, carted, failed
        # header
        headers = {
                'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                }

        # request session
        s = requests.Session()
        # login thru get request
        Logger.normal(f"[{self.username}] Logging In")
        r = s.get(login)   
        soup = bs(r.text,'lxml')
        #csrf token fetch
        try:
            csrf_token = soup.select_one('meta[name="csrf-token"]')['content']
        except AttributeError:
            Logger.error(f"[{self.username}] Error Fetching CSRF Token")
        # Cookie Fetch
        cookies = r.cookies
        # Login Payload
        data = {
            "CredentialForm[email]" : f"{self.username}",
            "CredentialForm[password_curr]" : f"{self.password}",
            "_csrf":f"{csrf_token}",
            "btn_login" : "Login",  
        }
        # POST Login Payload
        try:
            # POST Login URL
            r = s.post(login, cookies=cookies, data=data, headers=headers)
            soup = bs(r.text,'lxml')
            # Finding "Client Element" to see if the Login was successful
            try:
                element = soup.find("h1", {"id" : "online-page-header"})
            except AttributeError:
                Logger.error(f"[{self.username}] Error Fetching Header: Login Issue")

            if element.text == "Client":
                Logger.success(f"[{self.username}] Successfully Logged In [{r.status_code}]")
                ctypes.windll.kernel32.SetConsoleTitleW(f"OSCAR BOT {version} | {launcher} | Thread(s): {threads} | Delay: {delay} | Sleeping: {sleeping} | Carted: {carted} | Failed: {failed}")
                # clientname data used for payload value
                clientname = (soup.find("span",class_="client-name")).text
                Logger.normal(f"[{self.username}] Fetching Payload Data")

                # GET request for the Event Booking Page
                r = s.get(get_eventid.url)
                soup = bs(r.text,'lxml')
                # Important Values for payload
                try:
                    eventid2 = (soup.select_one('input[name="EventId"]')["value"])
                    token = soup.select_one('input[name="__RequestVerificationToken"]')['value']
                    priceid = soup.find(id='ParticipantsFamily_FamilyMembers_0__PriceTypeId')['value']
                    widgetid = soup.find(id='EventInfo_WidgetId')['value']
                    regformid = soup.find(id='EventInfo_RegFormId')['value']
                    calendarid = soup.find(id='EventInfo_CalendarId')['value']
                    programid = soup.find(id='EventInfo_ProgramId')['value']
                    date = soup.find(id="EventInfo_OccurrenceDate")['value']
                    contactid = soup.find(id='ParticipantsFamily_ReferralContactId')['value']
                    facilityid = soup.find(id='EventInfo_FacilityId')['value']
                    parentid = soup.find(id='EventInfo_ParentEventId')['value']
                    locationid = soup.find(id="EventInfo_LocationId")['value']
                except AttributeError:
                    Logger.error(f"[{self.username}] Error Fetching Payload Data")
                # Payload Dict
                data = [
                    ('__RequestVerificationToken', f'{token}'),
                    ('EventInfo.WidgetId', f'{widgetid}'),
                    ('EventInfo.RegFormId', f'{regformid}'),
                    ('EventInfo.CalendarId', f'{calendarid}'),
                    ('EventInfo.ProgramId', f'{programid}'),
                    ('EventInfo.ServiceDurationId', ''),
                    ('EventInfo.LocationId', f'{locationid}'),
                    ('EventInfo.Instructor.Id', ''),
                    ('EventInfo.AppointmentStartDateTimeTicks', '0'),
                    ('EventInfo.OccurrenceDate', f'{date}'),
                    ('ParticipantsFamily.ReferralContactId', f'{contactid}'),
                    ('EventInfo.FacilityId', f'{facilityid}'),
                    ('EventInfo.IgnoreEventCapacity', 'False'),
                    ('EventInfo.ParentEventId', f'{parentid}'),
                    ('LandingPageBackUrl', ''),
                    ('SkipRegistrationForm', 'False'),
                    ('WaitListMode', 'False'),
                    ('AmendmentMode', 'False'),
                    ('AmendmentInitiatorId', ''),
                    ('ParticipantsFamily.EventId', f'{eventid2}'),
                    ('ParticipantsFamily.FamilyMembers[0].MemberId', f'{contactid}'),
                    ('ParticipantsFamily.FamilyMembers[0].AccountId', ''),
                    ('ParticipantsFamily.FamilyMembers[0].FullNameSimple', f'{clientname}'),
                    ('ParticipantsFamily.FamilyMembers[0].FamilyMembership', 'You'),
                    ('ParticipantsFamily.FamilyMembers[0].Photo', ''),
                    ('ParticipantsFamily.FamilyMembers[0].PriceTypeId', f'{priceid}'),
                    ('ParticipantsFamily.FamilyMembers[0].IsParticipating', 'true'),
                    ('ParticipantsFamily.FamilyMembers[0].IsParticipating', 'false'),
                    ('ParticipantsFamily.FamilyMembers[0].AttendanceStatus', ''),
                ]
               
                if timed_event == "y":
                    # timed event: sleeps tasks
                    Logger.other(f"[{self.username}] Sleeping for: {timer.timer(user_time)} second(s)...")
                    sleeping+=1
                    ctypes.windll.kernel32.SetConsoleTitleW(f"OSCAR BOT {version} | {launcher} | Thread(s): {threads} | Delay: {delay} | Sleeping: {sleeping} | Carted: {carted} | Failed: {failed}")
                    await asyncio.sleep(timer.timer(user_time))
                    sleeping-=1
                    ctypes.windll.kernel32.SetConsoleTitleW(f"OSCAR BOT {version} | {launcher} | Thread(s): {threads} | Delay: {delay} | Sleeping: {sleeping} | Carted: {carted} | Failed: {failed}")
                    # Timed Event: ATC process
                    while True:
                        Logger.normal(f"[{self.username}] ATC...")
                        # GET request for the Event Booking Page
                        r = s.get(get_eventid.url)
                        soup = bs(r.text,'lxml')
                        # Important Values for payload
                        try:
                            eventid2 = (soup.select_one('input[name="EventId"]')["value"])
                            token = soup.select_one('input[name="__RequestVerificationToken"]')['value']
                            priceid = soup.find(id='ParticipantsFamily_FamilyMembers_0__PriceTypeId')['value']
                            widgetid = soup.find(id='EventInfo_WidgetId')['value']
                            regformid = soup.find(id='EventInfo_RegFormId')['value']
                            calendarid = soup.find(id='EventInfo_CalendarId')['value']
                            programid = soup.find(id='EventInfo_ProgramId')['value']
                            date = soup.find(id="EventInfo_OccurrenceDate")['value']
                            contactid = soup.find(id='ParticipantsFamily_ReferralContactId')['value']
                            facilityid = soup.find(id='EventInfo_FacilityId')['value']
                            parentid = soup.find(id='EventInfo_ParentEventId')['value']
                            locationid = soup.find(id="EventInfo_LocationId")['value']
                        except AttributeError:
                            Logger.error(f"[{self.username}] Error Fetching Payload Data")
                        # Payload Dict
                        data = [
                            ('__RequestVerificationToken', f'{token}'),
                            ('EventInfo.WidgetId', f'{widgetid}'),
                            ('EventInfo.RegFormId', f'{regformid}'),
                            ('EventInfo.CalendarId', f'{calendarid}'),
                            ('EventInfo.ProgramId', f'{programid}'),
                            ('EventInfo.ServiceDurationId', ''),
                            ('EventInfo.LocationId', f'{locationid}'),
                            ('EventInfo.Instructor.Id', ''),
                            ('EventInfo.AppointmentStartDateTimeTicks', '0'),
                            ('EventInfo.OccurrenceDate', f'{date}'),
                            ('ParticipantsFamily.ReferralContactId', f'{contactid}'),
                            ('EventInfo.FacilityId', f'{facilityid}'),
                            ('EventInfo.IgnoreEventCapacity', 'False'),
                            ('EventInfo.ParentEventId', f'{parentid}'),
                            ('LandingPageBackUrl', ''),
                            ('SkipRegistrationForm', 'False'),
                            ('WaitListMode', 'False'),
                            ('AmendmentMode', 'False'),
                            ('AmendmentInitiatorId', ''),
                            ('ParticipantsFamily.EventId', f'{eventid2}'),
                            ('ParticipantsFamily.FamilyMembers[0].MemberId', f'{contactid}'),
                            ('ParticipantsFamily.FamilyMembers[0].AccountId', ''),
                            ('ParticipantsFamily.FamilyMembers[0].FullNameSimple', f'{clientname}'),
                            ('ParticipantsFamily.FamilyMembers[0].FamilyMembership', 'You'),
                            ('ParticipantsFamily.FamilyMembers[0].Photo', ''),
                            ('ParticipantsFamily.FamilyMembers[0].PriceTypeId', f'{priceid}'),
                            ('ParticipantsFamily.FamilyMembers[0].IsParticipating', 'true'),
                            ('ParticipantsFamily.FamilyMembers[0].IsParticipating', 'false'),
                            ('ParticipantsFamily.FamilyMembers[0].AttendanceStatus', ''),
                        ]
               
                        # POST Fill Form
                        r=s.post(form, headers=headers, cookies=cookies, data=data)
                        soup = bs(r.text,'lxml')

                        # This element will determine whether or not session had ATC'd
                        element = soup.find("h2", {"id" : "bm-form-header"})

                        # if element is not found, retry [3 Attempts before terminating]
                        if element is None:
                            failed+=1
                            ctypes.windll.kernel32.SetConsoleTitleW(f"OSCAR BOT {version} | {launcher} | Thread(s): {threads} | Delay: {delay} | Sleeping: {sleeping} | Carted: {carted} | Failed: {failed}")
                            retry=0
                            while retry < 3:
                                Logger.error(f'[{self.username}] Error: Full / Not Opened! Retrying [{retry}]...')
                                wh("cart_hold","Error",self.username)
                                Logger.other(f"[{self.username}] Sleeping... [{delay}]")
                                await asyncio.sleep(int(delay))
                                Logger.normal(f"[{self.username}] Refreshing...")
                                r=s.post(form, headers=headers, cookies=cookies, data=data)
                                retry+=1
                            else:
                                Logger.error(f'[{self.username}] Error: Full / Not Opened! Terminating [{retry}]')
                                return False

                        # successfully carted lesgo
                        elif element.text == "DROP-IN - ADULT - OPEN GYM":
                            carted+=1
                            ctypes.windll.kernel32.SetConsoleTitleW(f"OSCAR BOT {version} | {launcher} | Thread(s): {threads} | Delay: {delay} | Sleeping: {sleeping} | Carted: {carted} | Failed: {failed}")
                            Logger.success(f"[{self.username}] Successfully Carted! [{r.status_code}]")
                            wh("cart_hold","Success",self.username)
                        Logger.other(f"[{self.username}] Sleeping... [{delay}]")
                        await asyncio.sleep(int(delay)) 
                        # GET request for the Event Booking Page
                        r = s.get(get_eventid.url)
                        soup = bs(r.text,'lxml')
                        # Important Values for payload
                        try:
                            eventid2 = (soup.select_one('input[name="EventId"]')["value"])
                            token = soup.select_one('input[name="__RequestVerificationToken"]')['value']
                            priceid = soup.find(id='ParticipantsFamily_FamilyMembers_0__PriceTypeId')['value']
                            widgetid = soup.find(id='EventInfo_WidgetId')['value']
                            regformid = soup.find(id='EventInfo_RegFormId')['value']
                            calendarid = soup.find(id='EventInfo_CalendarId')['value']
                            programid = soup.find(id='EventInfo_ProgramId')['value']
                            date = soup.find(id="EventInfo_OccurrenceDate")['value']
                            contactid = soup.find(id='ParticipantsFamily_ReferralContactId')['value']
                            facilityid = soup.find(id='EventInfo_FacilityId')['value']
                            parentid = soup.find(id='EventInfo_ParentEventId')['value']
                            locationid = soup.find(id="EventInfo_LocationId")['value']
                        except AttributeError:
                            Logger.error(f"[{self.username}] Error Fetching Payload Data")
                        # Payload Dict
                        data = [
                            ('__RequestVerificationToken', f'{token}'),
                            ('EventInfo.WidgetId', f'{widgetid}'),
                            ('EventInfo.RegFormId', f'{regformid}'),
                            ('EventInfo.CalendarId', f'{calendarid}'),
                            ('EventInfo.ProgramId', f'{programid}'),
                            ('EventInfo.ServiceDurationId', ''),
                            ('EventInfo.LocationId', f'{locationid}'),
                            ('EventInfo.Instructor.Id', ''),
                            ('EventInfo.AppointmentStartDateTimeTicks', '0'),
                            ('EventInfo.OccurrenceDate', f'{date}'),
                            ('ParticipantsFamily.ReferralContactId', f'{contactid}'),
                            ('EventInfo.FacilityId', f'{facilityid}'),
                            ('EventInfo.IgnoreEventCapacity', 'False'),
                            ('EventInfo.ParentEventId', f'{parentid}'),
                            ('LandingPageBackUrl', ''),
                            ('SkipRegistrationForm', 'False'),
                            ('WaitListMode', 'False'),
                            ('AmendmentMode', 'False'),
                            ('AmendmentInitiatorId', ''),
                            ('ParticipantsFamily.EventId', f'{eventid2}'),
                            ('ParticipantsFamily.FamilyMembers[0].MemberId', f'{contactid}'),
                            ('ParticipantsFamily.FamilyMembers[0].AccountId', ''),
                            ('ParticipantsFamily.FamilyMembers[0].FullNameSimple', f'{clientname}'),
                            ('ParticipantsFamily.FamilyMembers[0].FamilyMembership', 'You'),
                            ('ParticipantsFamily.FamilyMembers[0].Photo', ''),
                            ('ParticipantsFamily.FamilyMembers[0].PriceTypeId', f'{priceid}'),
                            ('ParticipantsFamily.FamilyMembers[0].IsParticipating', 'true'),
                            ('ParticipantsFamily.FamilyMembers[0].IsParticipating', 'false'),
                            ('ParticipantsFamily.FamilyMembers[0].AttendanceStatus', ''),
                        ] 
                        carted-=1
                
                elif timed_event == "n":
                    # non timed event
                    while True:
                        Logger.normal(f"[{self.username}] ATC...")
                        # POST request on FillForm URL
                        r=s.post(form, headers=headers, cookies=cookies, data=data)
                        soup = bs(r.text,'lxml')
                        # Check to see if successfully carted
                        element = soup.find("h2", {"id" : "bm-form-header"})
                        if element is None:
                            failed+=1
                            ctypes.windll.kernel32.SetConsoleTitleW(f"OSCAR BOT {version} | {launcher} | Thread(s): {threads} | Delay: {delay} | Sleeping: {sleeping} | Carted: {carted} | Failed: {failed}")
                            retry=0
                            while retry < 3:
                                Logger.error(f'[{self.username}] Error: Full / Not Opened! Retrying [{retry}]...')
                                wh("cart_hold","Error",self.username)
                                Logger.other(f"[{self.username}] Sleeping... [{delay}]")
                                await asyncio.sleep(int(delay))
                                Logger.normal(f"[{self.username}] Refreshing...")
                                r=s.post(form, headers=headers, cookies=cookies, data=data)
                                retry+=1
                            else:
                                Logger.error(f'[{self.username}] Error: Full / Not Opened! Terminating [{retry}]')
                                return False
                        
                        if element.text == "DROP-IN - ADULT - OPEN GYM":
                            carted+=1
                            ctypes.windll.kernel32.SetConsoleTitleW(f"OSCAR BOT {version} | {launcher} | Thread(s): {threads} | Delay: {delay} | Sleeping: {sleeping} | Carted: {carted} | Failed: {failed}")
                            Logger.success(f"[{self.username}] Successfully Carted! [{r.status_code}]")
                            wh("cart_hold","Success",self.username)

                        Logger.other(f"[{self.username}] Sleeping... [{delay}]")
                        await asyncio.sleep(int(delay))  
                        # GET request for the Event Booking Page
                        r = s.get(get_eventid.url)
                        soup = bs(r.text,'lxml')
                        # Important Values for payload
                        try:
                            eventid2 = (soup.select_one('input[name="EventId"]')["value"])
                            token = soup.select_one('input[name="__RequestVerificationToken"]')['value']
                            priceid = soup.find(id='ParticipantsFamily_FamilyMembers_0__PriceTypeId')['value']
                            widgetid = soup.find(id='EventInfo_WidgetId')['value']
                            regformid = soup.find(id='EventInfo_RegFormId')['value']
                            calendarid = soup.find(id='EventInfo_CalendarId')['value']
                            programid = soup.find(id='EventInfo_ProgramId')['value']
                            date = soup.find(id="EventInfo_OccurrenceDate")['value']
                            contactid = soup.find(id='ParticipantsFamily_ReferralContactId')['value']
                            facilityid = soup.find(id='EventInfo_FacilityId')['value']
                            parentid = soup.find(id='EventInfo_ParentEventId')['value']
                            locationid = soup.find(id="EventInfo_LocationId")['value']
                        except AttributeError:
                            Logger.error(f"[{self.username}] Error Fetching Payload Data")
                        # Payload Dict
                        data = [
                            ('__RequestVerificationToken', f'{token}'),
                            ('EventInfo.WidgetId', f'{widgetid}'),
                            ('EventInfo.RegFormId', f'{regformid}'),
                            ('EventInfo.CalendarId', f'{calendarid}'),
                            ('EventInfo.ProgramId', f'{programid}'),
                            ('EventInfo.ServiceDurationId', ''),
                            ('EventInfo.LocationId', f'{locationid}'),
                            ('EventInfo.Instructor.Id', ''),
                            ('EventInfo.AppointmentStartDateTimeTicks', '0'),
                            ('EventInfo.OccurrenceDate', f'{date}'),
                            ('ParticipantsFamily.ReferralContactId', f'{contactid}'),
                            ('EventInfo.FacilityId', f'{facilityid}'),
                            ('EventInfo.IgnoreEventCapacity', 'False'),
                            ('EventInfo.ParentEventId', f'{parentid}'),
                            ('LandingPageBackUrl', ''),
                            ('SkipRegistrationForm', 'False'),
                            ('WaitListMode', 'False'),
                            ('AmendmentMode', 'False'),
                            ('AmendmentInitiatorId', ''),
                            ('ParticipantsFamily.EventId', f'{eventid2}'),
                            ('ParticipantsFamily.FamilyMembers[0].MemberId', f'{contactid}'),
                            ('ParticipantsFamily.FamilyMembers[0].AccountId', ''),
                            ('ParticipantsFamily.FamilyMembers[0].FullNameSimple', f'{clientname}'),
                            ('ParticipantsFamily.FamilyMembers[0].FamilyMembership', 'You'),
                            ('ParticipantsFamily.FamilyMembers[0].Photo', ''),
                            ('ParticipantsFamily.FamilyMembers[0].PriceTypeId', f'{priceid}'),
                            ('ParticipantsFamily.FamilyMembers[0].IsParticipating', 'true'),
                            ('ParticipantsFamily.FamilyMembers[0].IsParticipating', 'false'),
                            ('ParticipantsFamily.FamilyMembers[0].AttendanceStatus', ''),
                        ] 
                        carted-=1
            else:
                Logger.error(f"[{self.username}] Login Error")

        except Exception as e:
            Logger.error(f"[{self.username}] {e}")

        finally:
            await asyncio.sleep(1.5)
            # Removes item from our queue
            queue_.get()
            queue_.task_done()
            ctypes.windll.kernel32.SetConsoleTitleW(f"OSCAR BOT {version} | {launcher} | Thread(s): {threads} | Delay: {delay} | Sleeping: {sleeping} | Carted: {carted} | Failed: {failed}")

# Menu Interface
if __name__ == '__main__':
    while True:
        print(f"{Fore.WHITE}[1] Cart Hold\n[2] Parse EventId\n[3] Settings\n[4] Exit\n")
        selection = input("Input: ")
        print("\n")

        # Cart Mode (1)
        if selection == "1": 
            print("Cart Hold Mode")
            eventid = input("Input Event ID: ")
            get_eventid.get_eventid(eventid)
            profile_count()
            timed_event = input(f"{Fore.WHITE}Timed Event? [Y] | [N]: ").lower() 
            inits()

            if timed_event == "y":
                user_time = input("Input Time [HH:MM:SS]: ")
                timer.timer(user_time)
                for i in range(profiles):
                    get_profiles(i)
                    CartHold(username,password)
                queue_.join()
            
            if timed_event == "n":
                for i in range(profiles):
                    get_profiles(i)
                    CartHold(username,password)
                queue_.join()

        # Event Id Parser
        elif selection == "2":
            url = input(str("Input URL: "))
            try:
                id = re.split('classId=|&occurrenceDate',url)[1]
                print("\n"+id+"\n")
                pass 
            except IndexError:
                pass

        # Settings
        elif selection == "3":
            print("View Settings\n")
            setting_list=[]
            with open("./data/settings.json", "r+") as settings:
                data = json.load(settings)
                for index,key in enumerate(data,start=1):
                    setting_list.append(key)
                    print(f"[{index}] {key}: {data[key]}")
                print(f"[{index+1}] Test Webhook\n[{index+2}] Go Back")  
                edit_settings = input("\nInput: ")
                if edit_settings == f'{index-5}':
                    edit_ = input(f"\n{setting_list[index-6]}: ")
                    data[setting_list[index-6]] = int(edit_)
                    settings.seek(0)
                    settings.truncate()
                    json.dump(data, settings,indent=4)
                elif edit_settings == f'{index-4}':
                    edit_ = input(f"\n{setting_list[index-5]}: ").lower()
                    data[setting_list[index-5]] = bool(edit_)
                    settings.seek(0)
                    settings.truncate()
                    json.dump(data, settings,indent=4)
                elif edit_settings == f'{index-3}':
                    edit_ = input(f"\n{setting_list[index-4]}: ").lower()
                    data[setting_list[index-4]] = bool(edit_)
                    settings.seek(0)
                    settings.truncate()
                    json.dump(data, settings,indent=4)
                elif edit_settings == f'{index-2}':
                    edit_ = input(f"\n{setting_list[index-3]}: ")
                    data[setting_list[index-3]] = str(edit_)
                    settings.seek(0)
                    settings.truncate()
                    json.dump(data, settings,indent=4)
                elif edit_settings == f'{index-1}':
                    edit_ = input(f"\n{setting_list[index-2]}: ")
                    data[setting_list[index-2]] = int(edit_)
                    settings.seek(0)
                    settings.truncate()
                    json.dump(data, settings,indent=4)    
                elif edit_settings == f'{index}':
                    edit_ = input(f"\n{key}: ")
                    data[setting_list[index-1]] = int(edit_)
                    settings.seek(0)
                    settings.truncate()
                    json.dump(data, settings,indent=4)   
                elif edit_settings == f'{index+1}':
                    with open("./data/settings.json", "r") as settings:
                        data = json.loads(settings.read())
                        wh_ = data['webhook']
                    wh("test_wh","Success","200")
                elif edit_settings == f'{index+2}':
                    continue
                else:
                    pass
        
        # Exit
        elif selection == "4":
            print("Exiting")
            sys.exit()
        
        # Cart Mode (2)
        if selection == "5": 
            print("Cart Hold Mode")
            eventid = input("Input Event ID: ")
            get_eventid.get_eventid(eventid)
            profile_count()
            timed_event = input(f"{Fore.WHITE}Timed Event? [Y] | [N]: ").lower() 
            inits()

            if timed_event == "y":
                user_time = input("Input Time [HH:MM:SS]: ")
                timer.timer(user_time)
                for i in range(profiles):
                    get_profiles(i)
                    CartHold2(username,password)
                queue_.join()
            
            if timed_event == "n":
                for i in range(profiles):
                    get_profiles(i)
                    CartHold2(username,password)
                queue_.join()
        else:
            pass