from datetime import datetime
def timer(user_time):
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
        