"""
Skrypt sprawdzajacy bledy / wyjatki minerow i slacy notyfikacje na kanal discord
    Uruchomienie:
    1. uzupelniamy swoj webhook kanalu discord: WEB_HOOK
    2. instalacja: pip3 install discord_webhook && pip3 install rich && 
    3. uruchomienie sesji TMUX: tmux new -tmonit
    4. (opcja) na podzie ustawiamy zmienna srodowiskowa RUNPOD_POD_TBNM, np: export RUNPOD_POD_TBNM = "6000_01"
    5. (opcja) w skrypcie ustawiamy nazwe karty jako stala CARD_NAME
    6. Przejscie do katalogu bt_tools: cd /workspace/bt_tools
    6. Uruchomienie skryptu: python3 error_notif.py
    7. Wyjscie z sesji monitorujacej tmux: ctrl + d (command + d)

2022-11-17 tiba
"""
import json
import subprocess
import os
from rich import print
import time
from datetime import datetime, timedelta
from discord_webhook import DiscordWebhook
CARD_NAME=""
WEB_HOOK = "https://discord.com/api/webhooks/1028636237248081940/u9ukX33R6L7erkx0ewoSwwBbcA3y2ovd56P-dqltxHZHcv5sbsu1Z3tZx6auPHVD0nrl"

runpod_id=os.environ.get('RUNPOD_POD_ID', "")
card_name=os.environ.get('RUNPOD_POD_TBNM', CARD_NAME)

print( datetime.strftime(datetime.today(),"%Y-%m-%d %H:%M:%S") + ": " + card_name + " " +  runpod_id + " error & exception monitor started. Webhook used:\n" +  WEB_HOOK)

# Create json directory for pm2 statuses
current_dir = os.getcwd()
json_dir = current_dir + "/json"

if not os.path.exists(json_dir):
   os.makedirs(json_dir)
   print("json dir created")

while True:
    # Prepare pm2 process data for parsing
    command0 = ["pm2 jlist > " + json_dir + "/pm2_jlist_errnotif.json"]
    with subprocess.Popen(command0, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
            , shell=True) as proc:
        cmd0_out = proc.stdout.read()
        if(not cmd0_out):
            pass
        else:
            print(cmd0_out)

    try:
        jsonFile = open(json_dir + "/pm2_jlist_errnotif.json")
    except IOError:
        print("ERROR: Opening file\n")
        raise SystemExit

    data = json.load(jsonFile)

    for dataItem in data:

        try:
            args = dataItem["pm2_env"]["args"]
            #pm2 process data
            pm_name = str(dataItem["name"])
            pm_status = str(dataItem["pm2_env"]["status"])
            infoString = ""
        
        #Display exceptions from pm2 standard logs
        #60 lines: ~ 5-7 minutes      tail -60 /root/.pm2/logs/miner32-out.log
            command10 = ["tail -60 /root/.pm2/logs/" + str(dataItem["name"]) + "-out.log | awk '/xception/ {$1=$4=$5=$8=$10=$19=$20=\"\"; print}' | sed -r \"s/\x1B\[([0-9]{1,3}((;[0-9]{1,3})*)?)?[m|K]//g\" | cut -c -160 | grep -Fv -e \" is not in list\""]
            #command10 = ["tail -80 /workspace/logs/mtest27-out.log | awk '/xception/ {$1=$4=$5=$8=$10=$19=$20=\"\"; print}' | sed -r \"s/\x1B\[([0-9]{1,3}((;[0-9]{1,3})*)?)?[m|K]//g\" | cut -c -160 | grep -Fv -e \" is not in list\""]
            with subprocess.Popen(command10, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
                    , shell=True) as proc:
                cmd10_out = proc.stdout.read()
                cmd10_out = cmd10_out.replace('\n\n', '\n')

                if(not cmd10_out):
                    continue
                else:
                    msg = card_name + " " +  runpod_id + " " +  pm_name + " (" + pm_status + ") exceptions:\n"
                    msg = msg + cmd10_out
                    print(msg)
                    webhook = DiscordWebhook(url=WEB_HOOK, content=msg)
                    response = webhook.execute()

        ##Display errors from pm2 error logs
            command20 = ['tail -1 /root/.pm2/logs/' + str(dataItem["name"]) + '-error.log']
            #command20 = ['tail -1 /workspace/logs/mtest27-error.log']
            with subprocess.Popen(command20, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
                    , shell=True) as proc:
                cmd20_out = datetime.strptime(proc.stdout.read()[0:19],"%Y-%m-%dT%H:%M:%S")
            
            if cmd20_out >= datetime.today() - timedelta(minutes=120):
                command30 = ['tail -7 /root/.pm2/logs/' + str(dataItem["name"]) + '-error.log | grep -Fv -e "Using pad_token" -e "config_info = json_normalize" -e "KeyboardInterrupt" -e "───────────" -e "json_normalize is deprecated" -e "�─╯ │" -e ": │" -e ": ╭" -e ": ╰"']
                #command30 = ['tail -7 /workspace/logs/mtest27-error.log |                       grep -Fv -e "Using pad_token" -e "config_info = json_normalize" -e "KeyboardInterrupt" -e "───────────" -e "json_normalize is deprecated" -e "�─╯ │" -e ": │" -e ": ╭" -e ": ╰"']
                with subprocess.Popen(command30, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
                        , shell=True) as proc:
                    cmd30_out = proc.stdout.read()

                    if(not cmd30_out):
                        continue
                    else:
                        msg_err = card_name + " " +  runpod_id + " " +  pm_name + " (" + pm_status + ") errors:\n"
                        msg_err = msg_err + cmd30_out
                        print(msg_err)
                        webhook = DiscordWebhook(url=WEB_HOOK, content=msg_err)
                        response = webhook.execute()

            else: 
                continue
                #print( "[green]Last errors older than [/green]" + str(cmd20_out))
        except KeyError:
            pm_name = str(dataItem["name"])
            #print(pm_name + " process has no args")

    jsonFile.close()
    time.sleep(300)
    ### end loop


#  grep -Fv -e ": │" -e ": ╭" -e ": ╰" /root/.pm2/logs/miner32-error.log
# Examples"
#2022-11-16T13:12:10: RuntimeError: CUDA registration is enabled but no CUDA devices are detected.
#2022-11-16T13:11:37: WebSocketConnectionClosedException: socket is already closed.
###Ignore:
#2022-11-10T10:32:39: ValueError: '5EvrPnJnw1s2mUbPUYpoXJ5RNsbBwmyx9U5KUEb5BFTtaPs3' is not in list
#2022-11-10T10:33:15: KeyboardInterrupt
#2022-11-10T10:32:47: Using pad_token, but it is not set yet.
#2022-11-10T10:35:22: /root/.bittensor/bittensor/bittensor/_config/config_impl.py:61: FutureWarning: pandas.io.json.json_normalize is deprecated, use pandas.json_normalize instead
#2022-11-14T17:58:06:   config_info = json_normalize(json.loads(json.dumps(self)), sep='.').to_dict(orient='records')[0]
#2022-11-06T12:09:41: atures=4096, bias=True)
#Downloading 