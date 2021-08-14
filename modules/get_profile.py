import ctypes,csv,json
def get_profile(n):
    global username,password,user_sig,cc_num,cc_ccv,cc_strt,cc_city,cc_zip,cc_month,cc_year,cc_name
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

        ctypes.windll.kernel32.SetConsoleTitleW(f"{username} | OSCAR AIO {version}")
        return username,password,user_sig,cc_num,cc_ccv,cc_strt,cc_city,cc_zip,cc_month,cc_year,cc_name
