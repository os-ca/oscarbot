import ctypes, requests, json, csv, queue, threading, asyncio, platform, sys, subprocess, random, re, string
from datetime import datetime, timedelta

from requests.exceptions import ProxyError
from requests.auth import HTTPProxyAuth

try:
    from bs4 import BeautifulSoup as bs 
    from colorama import init, Fore
    import lxml
    
except ImportError:
    print("Import Error: Installing Dependencies")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'colorama'])
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'bs4'])
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'lxml']) 

# init stuff
version= "1.7.4"
launcher = "REQUEST"
init(convert=True) if platform.system() == "Windows" else init()
ctypes.windll.kernel32.SetConsoleTitleW(f"{version} | {launcher}")
# Payload values for fetching classes.svg
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
}

data = {
    'calendarId': 'f14c6c16-b80d-48dd-be79-aa664d2346b4',
    'widgetId': '15f6af07-39c5-473e-b053-96653f77a406',
    'page': '0',
    'dateString': '',
    '__RequestVerificationToken': 'HgRXPgCiZoFqhxqAvrLPxvDcykNaUtOFxtBpZwZsHUiR_nd1Og1SP6zIBMRFdB4Q0DQGDwdjha_OCJ-hQZXf4oAqeBURNokoOL1vwadaEvqdH-Br0'
    }

url = 'https://ubc.perfectmind.com/24063/Clients/BookMe4BookingPages/Classes'    

def id_gen(size=4, chars=string.ascii_uppercase + string.digits):
    """ randomly genned ids for task id, log id, etc"""
    return ''.join(random.choice(chars) for _ in range(size))

fetchedList, fetchedList2 = [], []
def inits():
    global use_proxies,wh_,eventid,threads,delay, timeout
    with open("./data/settings.json", "r") as settings:
        data = json.loads(settings.read())
        wh_ = data['webhook']
        threads = data['threads']
        use_proxies = data['use_proxies']
        delay = data['delay']
        timeout = data['timeout']
    
    # Proxies
    if use_proxies is True:
        global proxyList
        with open("./data/proxies.txt","r") as proxyfile:
            proxyfile.read().split('\n')

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
    @staticmethod
    def error2(message):
        print(f"{Fore.RED}{message}") 
    @staticmethod
    def n2(message):
        print(f"{orange}{message}") 

class Proxy:
    """ determines the proxy type and returns a random proxy respective type"""
    @staticmethod
    def get_proxy(proxyList):
        proxy = random.choice(proxyList)
        if len(proxy.split(":")) == 2:
            proxy_type = "IP"
        elif len(proxy.split(":")) == 4:
            proxy_type = "UP"
        else:
            Logger.error2("Invalid Proxy Format. Localhost default")
            proxy_type = "LH"
        # returns proxy and the type
        return proxy, proxy_type

class Headers:
    @staticmethod
    def chead():
        ctypes.windll.kernel32.SetConsoleTitleW(f"{version} | {launcher} | Thread(s): {threads} | Delay: {delay} | Sleeping: {sleeping} | Carted: {carted} | Failed: {failed}")

# constants
login = 'https://portal.recreation.ubc.ca/index.php?r=public%2Findex'
form = "https://ubc.perfectmind.com/24063/Menu/BookMe4RegistrationForms/FillForms"

def get_profiles(n):
    """ grabs bot_data.json values and profiles.csv """
    global username,password
    new_list = []
    with open("./data/profiles.csv",'r',newline='',encoding="utf-8-sig") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            new_list.extend([[row["username"],row['password']]])
        username,password = new_list[n][0],new_list[n][1]

def prof_count():
    """ returns profile count as int """
    with open("./data/profiles.csv",'r',newline='',encoding="utf-8-sig") as csvfile:
        reader = csv.DictReader(csvfile)
        profiles = int(len(list(reader))-1)
    return profiles

def get_eventid(eventid):
    """ returns url for the specific eventid"""
    event_id = eventid
    tmrw_ = (''.join(re.split('-',str(datetime.strptime(str((datetime.today()+timedelta(days=1)))[:10], "%Y-%m-%d").date()))))
    url = f"https://ubc.perfectmind.com/24063/Clients/BookMe4EventParticipants?eventId={event_id}&occurrenceDate={tmrw_}&&locationId=27a6cd2c-34a1-40f9-822e-cf70b5bca13c&waitListMode=False" 
    return url, event_id

def timer(user_time):
    """ timed event """
    today = datetime.now().time()
    d_start = datetime.strptime(str(today)[:-7], "%H:%M:%S")
    d_end = datetime.strptime(user_time, "%H:%M:%S")
    diff = (d_end-d_start).total_seconds()
    if diff < 0:
        print("Error: Negative Seconds. Returning Time.sleep(1)")
        diff = 1
        return diff
    else:
        return diff

def wh(method,checkout,username,course):
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
                            "value": f"{course}",
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

def BookPageFetch(taskid,clientname,r):
    """ fetches all payload values for booking page and unpacks all values into the data payload for the POST Request """
    
    soup = bs(r.text,'lxml')
    try:
        # fetching values for the specific username task
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

        # data payload
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
        return data
    except AttributeError:
        return Logger.error(f"[{taskid}] BookPageFetch: Error Fetching Payload Data")

class CartHold():
    def __init__(self,taskid,username,password,course):
        self.taskid,self.username,self.password,self.course = taskid,username,password,course
        queue_.put(self)
        threading.Thread(target=self.run).start()
    def run(self):
        asyncio.run(self.login_())

    async def login_(self):
        global sleeping, carted, failed    
        Headers.chead()

        # Logging stuff
        LOG_FILENAME = f'{self.taskid}_{datetime.utcnow().strftime("%Y_%m_%d_%H_%M_%S")}'
        log = open(f"./data/logs/{LOG_FILENAME}.txt", "w+")
        log.close()

        headers = {
            'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            }
        
        # request session
        s = requests.Session()
         
        # proxy statements
        if use_proxies is False:
            proxy = ['localhost']
        else:
            proxyList=[]
            with open("./data/proxies.txt", "r+") as f:
                if f.read() == "":
                    proxy = 'localhost'
                   
                else:
                    with open("./data/proxies.txt", "r+") as f:
                        for proxy in f:
                            proxyList.append(proxy)
                        proxy = Proxy.get_proxy(proxyList)

                        if proxy[1] == "IP":
                            proxies = {'https' : f'http://{proxy[0]}'}
                            s.proxies = proxies
                            proxy = re.split("\n",proxy[0])[0]
        
                        elif proxy[1] == "UP":
                            auth = HTTPProxyAuth(f"{proxy[0].split(':')[2]}",f"{proxy[0].split(':')[3]}")
                            proxies = {'http' : f"http://{proxy[0].split(':')[0]}:{proxy[0].split(':')[1]}"}
                            s.proxies = proxies
                            s.auth = auth
                            proxy = f"{proxy[0].split(':')[0]}:{proxy[0].split(':')[1]}"

                        elif proxy[1] == "LH":
                            proxy = 'localhost'
            
        
        # login thru get request
        try:
            Logger.normal(f"[{proxy}] [{self.taskid}] Logging In")
            r = s.get(login,timeout=timeout)   
        except ProxyError:
            failed+=1
            Headers.chead()
            return Logger.error(f"[{proxy}] [{self.taskid}] Proxy Error")
            
        except Exception as e:
            failed+=1
            Headers.chead()
            return Logger.error(f"[{proxy}] [{self.taskid}] Error at Log in: {e}")
            
        except TimeoutError:
            failed+=1
            Headers.chead()
            return Logger.error(f"[{proxy}] [{self.taskid}] Timed out!")
        
        soup = bs(r.text,'lxml')
        #csrf token fetch
        try:
            csrf_token = soup.select_one('meta[name="csrf-token"]')['content']
        except AttributeError:
            failed+=1
            Headers.chead()
            return Logger.error(f"[{proxy}] [{self.taskid}] Error Fetching CSRF Token")
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
            r = s.post(login, cookies=cookies, data=data, headers=headers, timeout=timeout)
            soup = bs(r.text,'lxml')
            # Finding "Client Element" to see if the Login was successful
            try:
                element = soup.find("h1", {"id" : "online-page-header"})
            except AttributeError:
                failed+=1
                Headers.chead()
                return Logger.error(f"[{proxy}] [{self.taskid}] Error Fetching Header: Login Issue")

            if element.text == "Client":
                Logger.success(f"[{proxy}] [{self.taskid}] Successfully Logged In [{r.status_code}]")

                # clientname data used for payload value
                clientname = (soup.find("span",class_="client-name")).text

                # GET request for the Event Booking Page and returns all payload values
                Logger.normal(f"[{proxy}] [{self.taskid}] Fetching Payload Data")
                url = get_eventid(self.course)
                r = s.get(url[0], timeout=timeout)
                data = BookPageFetch(self.taskid, clientname, r)
                
                # non timed event
                while True:
                    try:
                        Logger.normal(f"[{proxy}] [{self.taskid}] ATC...")
                        # POST request on FillForm URL
                        r=s.post(form, headers=headers, cookies=cookies, data=data)
                    except Exception as e:
                        failed+=1
                        Headers.chead()
                        return Logger.error(f"[{self.taskid}] ATC Error: {e}")
                    soup = bs(r.text,'html.parser')
                    # Check to see if successfully carted
                    element = soup.find("h2", {"id" : "bm-form-header"})
                    if element is None:
                        retry=0
                        while retry < 9999999:
                            Logger.error(f'[{proxy}] [{self.taskid}] Error: Full / Not Opened! Retrying ({retry})...')
                            failed+=1
                            Headers.chead()
                            wh("cart_hold","Error",self.username,self.course)
                            Logger.other(f"[{proxy}] [{self.taskid}] Sleeping... ({delay}s)")
                            await asyncio.sleep(int(delay))
                            Logger.normal(f"[{proxy}] [{self.taskid}] Refreshing...")
                            failed-=1
                            try: 
                                r=s.post(form, headers=headers, cookies=cookies, data=data, timeout=timeout)
                                retry+=1
                            except TimeoutError:
                                failed+=1
                                Headers.chead()
                                return Logger.error(f"[{proxy}] [{self.taskid}] Timed out!")
                        else:
                            failed+=1
                            Headers.chead()
                            Logger.error(f'[{proxy}] [{self.taskid}] Error: Full / Not Opened! Terminating ({retry})')
                            return False
                    
                    if element.text == "DROP-IN - ADULT - OPEN GYM":
                        carted+=1
                        Headers.chead()
                        Logger.success(f"[{proxy}] [{self.taskid}] Successfully Carted! [{r.status_code}]")
                        wh("cart_hold","Success",self.username,self.course)

                    Logger.other(f"[{proxy}] [{self.taskid}] Sleeping... ({delay}s)")
                    await asyncio.sleep(int(delay))  
                    # GET request for the Event Booking Page
                    try:
                        r = s.get(url[0], timeout=timeout)
                    except TimeoutError:
                        failed+=1
                        Headers.chead()
                        return Logger.error(f"[{proxy}] [{self.taskid}] Timed out!")
                    data = BookPageFetch(self.username,clientname,r)
                    carted-=1

            else:
                failed+=1
                Headers.chead()
                Logger.error(f"[{proxy}] [{self.taskid}] Login Error")

        except Exception as e:
            failed+=1
            Headers.chead()
            Logger.error(f"[{proxy}] [{self.taskid}] Exception Error: {e}")

        except TimeoutError:
            failed+=1
            Headers.chead()
            return Logger.error(f"[{proxy}] [{self.taskid}] Timed out!")

        finally:
            await asyncio.sleep(1.5)
            # Removes item from our queue
            with open(f'./data/logs/logs_{self.taskid}_{datetime.utcnow().strftime("%Y_%m_%d_%H_%M_%S")}.txt','w+') as f:
                f.write("d")
                
            queue_.get()
            queue_.task_done()

# fetch module for fetching basketball timeslots in the classes.svg
def fetch(url,headers,data):
    print("Fetching Timeslots")
    if use_proxies:
        try:
            proxyList=[]
            with open("./data/proxies.txt", "r+") as f:
                # if proxies.txt is empty -> will POST request on localhost
                if f.read() == "":
                    try:
                        response = requests.post(url, headers=headers, data=data, timeout=timeout)
                    except Exception as e:
                        return print(f"Error fetching classes.svg: {e}")
                else:
                    with open("./data/proxies.txt", "r+") as f:
                        # if proxies.txt has proxies -> will POST request on a random proxy
                        for proxy in f:
                            proxyList.append(proxy)
                        proxy = Proxy.get_proxy(proxyList)
                        try:
                            if proxy[1] == "IP":
                                proxies = {'https' : f'http://{proxy[0]}'}
                                response = requests.post(url, headers=headers, data=data, proxies=proxies, timeout=timeout)
                            elif proxy[1] == "UP":
                                auth = HTTPProxyAuth(f"{proxy[0].split(':')[2]}",f"{proxy[0].split(':')[3]}")
                                proxies = {'http' : f"http://{proxy[0].split(':')[0]}:{proxy[0].split(':')[1]}"}
                                response = requests.post(url, headers=headers, data=data, proxies=proxies, auth=auth, timeout=timeout)
                            elif proxy[1] == "LH":
                                response = requests.post(url, headers=headers, data=data, timeout=timeout)
                        except ProxyError:
                            return Logger.error2(f"Proxy Error {proxy}")
                        except TimeoutError:
                            return Logger.error2("Timed Out!")
                            
                    
            proxy = re.split("\n",proxy[0])
            classData = json.loads(response.text)['classes']
            for data in classData:
                if data["EventName"] == "REGISTER | Basketball Member/Student Access":
                    if data["Spots"] == "":
                        data["Spots"] = "null"
                    fetchedList.extend([[data['FormattedStartDate'],data['EventTimeDescription'],data['Spots'],data['EventId']]])
            return fetchedList

        except TimeoutError:
            return Logger.error2(f"[{proxy}] Timed Out!")
        except Exception as e:
            return Logger.error2(f"[{proxy}] Fetching Error: {e}")
        
    else:
        response = requests.post(url, headers=headers, data=data)
        classData = json.loads(response.text)['classes']
        for data in classData:
            if data["EventName"] == "REGISTER | Basketball Member/Student Access":
                if data["Spots"] == "":
                    data["Spots"] = "null"
                fetchedList.extend([[data['FormattedStartDate'],data['EventTimeDescription'],data['Spots'],data['EventId']]])
        return fetchedList

def main():
    while True:
        print(f"{Fore.WHITE}[1] Cart Hold\n[2] Exit\n")
        selection = input("Input: ")
        print("\n")

        # Cart Mode (1)
        if selection == "1": 
            print("Cart Hold Mode\nInitialising\n")
            inits()
            # fetching all courses in classes.svg
            fetchedList = fetch(url,headers,data)
            if fetchedList is None:
                import time
                Logger.error2("\nFetched Nothing: Terminating in 5 seconds!")
                time.sleep(5)
                break
            else:
                for key,courses in enumerate(fetchedList):
                    print(key,courses)
                eventid = input("Input Index Number: ")
                selectedCourse = fetchedList[int(eventid)]
                Logger.n2(f"{selectedCourse[3]} Selected\n")
                fetchedList.clear()
                for i in range(prof_count()):
                    get_profiles(i)
                    CartHold(id_gen(),username,password,selectedCourse[3])
                queue_.join()
        
        # Exit
        elif selection == "2":
            import os
            print("Exiting")
            try:
                os.system('taskkill /f /im launcher.exe /T')
            except FileNotFoundError:
                os.system('taskkill /f /im launcher.py /T')
            sys.exit()

        else:
            pass

# Menu Interface
if __name__ == '__main__':
    main()
