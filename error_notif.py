"""
Loop execution for notifications
    pip3 install discord_webhook 
    while true; do echo "Checking miner logs for exceptions" && python3 /workspace/error_notif.py; sleep 300s; done
2022-11-02 tiba
"""
import json
import subprocess
from rich import print
from datetime import datetime, timedelta
from discord_webhook import DiscordWebhook
CARD_NAME=""
DISCORD_WEBHOOK="TWOJ_WEBHOOK"
# Prepare pm2 process data for parsing
command0 = ["pm2 jlist > pm2_jlist.json"]
with subprocess.Popen(command0, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
        , shell=True) as proc:
   print(proc.stdout.read())

try:
    jsonFile = open("pm2_jlist.json")
except IOError:
    print("ERROR: Opening file\n")
    raise SystemExit

data = json.load(jsonFile)

for dataItem in data:
    args = dataItem["pm2_env"]["args"]
    #pm2 process data
    pm_name = str(dataItem["name"])
    pm_status = str(dataItem["pm2_env"]["status"])
    infoString = ""
#Display exceptions from pm2 standard logs tail -2000 /root/.pm2/logs/miner36-out.log
#tail -2000 /root/.pm2/logs/miner8-out.log | awk '/xception/ {$1=$4=$5=$8=$10=$19=$20=""; print}' | sed -r "s/\x1B\[([0-9]{1,3}((;[0-9]{1,3})*)?)?[m|K]//g" | cut -c -160 | grep -Fv -e " is not in list"
    command4 = ["tail -60 /root/.pm2/logs/" + str(dataItem["name"]) + "-out.log | awk '/xception/ {$1=$4=$5=$8=$10=$19=$20=\"\"; print}' | sed -r \"s/\x1B\[([0-9]{1,3}((;[0-9]{1,3})*)?)?[m|K]//g\" | cut -c -160 | grep -Fv -e \" is not in list\""]
    with subprocess.Popen(command4, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
            , shell=True) as proc:
        cmd4_out = proc.stdout.read()
        print(cmd4_out)
        if(not cmd4_out):
            continue
        else:
            msg = CARD_NAME +" " + pm_name + "(" + pm_status+ ") exceptions:\n"
            msg = msg + cmd4_out
            print(msg)
            webhook = DiscordWebhook(url='DISCORD_WEBHOOK'
                , content=msg)
            response = webhook.execute()
jsonFile.close()