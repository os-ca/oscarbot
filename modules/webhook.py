import requests, json
from datetime import datetime
from OscarAIO import Logger,version
from OscarAIObeta import Logger,version
from modules import get_eventid, get_profile
with open("./data/settings.json", "r") as settings:
    data = json.load(settings)
    wh_ = data['webhook']

def wh(method,checkout):
    if method  == "checkout_link":
        from modules import get_order
        data = {
                    "username" : "UBC MY BITCH"
                }
        data["embeds"] = [
                {
                    "title" : "Successful Checkout",
                    "timestamp": f"{datetime.utcnow()}",
                    "footer": {
                        "icon_url": "https://cdn.discordapp.com/attachments/854247964612493342/854494516269809664/1WlC-_yW_400x400.jpg",
                        "text": f"oscar aio {version}"
                    },
                    "fields": [
                        {
                            "name": "Event ID",
                            "value": f"{get_eventid.event_id}",
                            "inline": False
                        },
                        {
                            "name": "Order ID",
                            "value": f"{get_order.orderid1}",
                            "inline": False
                        },
                        {
                            "name": "Start Date",
                            "value": f"{get_order.bdate1}",
                            "inline": True
                        },
                        {
                            "name": "Time",
                            "value": f"{get_order.btime1}",
                            "inline": True
                        },
                        {
                            "name": "Name",
                            "value": f"{get_order.name1}",
                            "inline": True
                        },
                        {
                            "name": "Mode",
                            "value": f"{method}",
                            "inline": False
                        },
                        {
                            "name": "Checkout Link",
                            "value": f"{checkout}",
                            "inline": False
                        },
                    
                    ]
                    
                }
            ]
    elif method == "full_checkout":
        from modules import get_order
        data = {
                    "username" : "UBC MY BITCH"
                }
        data["embeds"] = [
                {
                    "title" : "Successful Checkout",
                    "timestamp": f"{datetime.utcnow()}",
                    "footer": {
                        "icon_url": "https://cdn.discordapp.com/attachments/854247964612493342/854494516269809664/1WlC-_yW_400x400.jpg",
                        "text": f"oscar aio {version}"
                    },
                    "fields": [
                        {
                            "name": "Event ID",
                            "value": f"{get_eventid.event_id}",
                            "inline": False
                        },
                        {
                            "name": "Order ID",
                            "value": f"{get_order.orderid1}",
                            "inline": False
                        },
                        {
                            "name": "Start Date",
                            "value": f"{get_order.bdate1}",
                            "inline": True
                        },
                        {
                            "name": "Time",
                            "value": f"{get_order.btime1}",
                            "inline": True
                        },
                        {
                            "name": "Name",
                            "value": f"{get_order.name1}",
                            "inline": True
                        },
                        {
                            "name": "Mode",
                            "value": f"{method}",
                            "inline": False
                        }
                    ]
                    
                }
            ]
    elif method == "checkout_error":
        from modules import get_order
        data = {
                    "username" : "UBC MY BITCH"
                }
        data["embeds"] = [
                {
                    "title" : "Payment Declined",
                    "timestamp": f"{datetime.utcnow()}",
                    "footer": {
                        "icon_url": "https://cdn.discordapp.com/attachments/854247964612493342/854494516269809664/1WlC-_yW_400x400.jpg",
                        "text": f"oscar aio {version}"
                    },
                    "fields": [
                        {
                            "name": "Event ID",
                            "value": f"{get_eventid.event_id}",
                            "inline": False
                        },
                        {
                            "name": "Order ID",
                            "value": f"{get_order.orderid1}",
                            "inline": False
                        },
                        {
                            "name": "Start Date",
                            "value": f"{get_order.bdate1}",
                            "inline": True
                        },
                        {
                            "name": "Time",
                            "value": f"{get_order.btime1}",
                            "inline": True
                        },
                        {
                            "name": "Name",
                            "value": f"{get_order.name1}",
                            "inline": True
                        },
                        {
                            "name": "Mode",
                            "value": f"{method}",
                            "inline": False
                        }
                    ]
                    
                }
            ]
    elif method  == "cart_hold":

        data = {
                    "username" : "UBC MY BITCH"
                }
        data["embeds"] = [
                {
                    "title" : f"Cart Hold {checkout}",
                    "timestamp": f"{datetime.utcnow()}",
                    "footer": {
                        "icon_url": "https://cdn.discordapp.com/attachments/854247964612493342/854494516269809664/1WlC-_yW_400x400.jpg",
                        "text": f"oscar aio {version}"
                    },
                    "fields": [
                        {
                            "name": "Event ID",
                            "value": f"{get_eventid.event_id}",
                            "inline": False
                        },
                        {
                            "name": "User",
                            "value": f"{get_profile.username}",
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
                        "text": f"oscar aio {version}"
                    }
                }           
            ]
                                 
    try:
        result = requests.post(wh_, json = data)   
        result.raise_for_status()   
    except requests.exceptions.HTTPError as e:
        Logger.error(e)
    else:
        Logger.success("Payload delivered successfully [{}]".format(result.status_code))