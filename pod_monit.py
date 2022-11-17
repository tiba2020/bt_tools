"""
Displaying basic bittensor core_server info on runpod based on pm2
Loop execution for online monitoring:
    while true; do clear && python3 /workspace/pod_monit.py; sleep 120s; done
For execution on startup:
    1. edit .bashrc file:
    nano ~/.bashrc
    2. paste at the end of the file:
    clear && python3 /workspace/pod_monit.py
TODOs: - sort pm2 data by pid 
       - merge nvidia memusage with pm2 data
2022-11-01
"""
import os
import json
import subprocess
from rich import print
from datetime import datetime, timedelta

MODEL_ARG = "--neuron.model_name"
SUBTENS_ARG = "--subtensor.chain_endpoint"
AXON_ARG = "--axon.port"
HOTKEY_ARG = "--wallet.hotkey"

def time_since_dttm( dttm=None ):
    """Calculates the time passed since a given dttm till now, formats as string"""
    if dttm == None:
        return "Incorrect argument: provide a datetime"

    try:
        uptime_dttm = datetime.today() - dttm
        up_secs_all = uptime_dttm.total_seconds()

        up_days = up_secs_all // 86400 
        # hours
        up_secs = up_secs_all - (up_days * 86400)
        up_hrs = up_secs // 3600 
        # minutes
        up_secs = up_secs - (up_hrs * 3600)
        up_mnts = up_secs // 60
        # remaining seconds
        up_secs = up_secs - (up_mnts * 60)
        # total time
        if up_secs_all < 3600:
            time_since = "{:02}:{:02}".format(int(up_mnts), int(up_secs))
        elif up_secs_all < 86400:
            time_since = "{:02}:{:02}:{:02}".format(int(up_hrs), int(up_mnts), int(up_secs))
        else:
            time_since = "{}d {:02}:{:02}".format(int(up_days), int(up_hrs), int(up_mnts))
    except ValueError:
        return "Incorrect value"

    return time_since

class Miner(object):
    def __init__(self, pm_name, pm_pid, pm_status, uptime, axon, model, subtensor, avg_loss, pm_uptime_ts):
        self.pm_name = pm_name
        self.pm_pid = pm_pid
        self.pm_status = pm_status
        self.uptime = uptime
        self.axon = axon
        self.subtensor = subtensor
        self.avg_loss = avg_loss
        self.model = model
        self.pm_uptime_ts = pm_uptime_ts

    def __str__(self):
        return "{0} {1} {2} {3} {4} {5} {6} {7}".format(self.pm_name, self.pm_pid, self.pm_status, self.uptime, self.axon, self.subtensor, self.avg_loss, self.model)

current_dir = os.getcwd()
json_dir = current_dir + "/json"

if not os.path.exists(json_dir):
   os.makedirs(json_dir)
   print("json dir created")

# prepare pm2 process data for parsing
command0 = ["pm2 jlist > " + json_dir + "/pm2_jlist_status.json"]
with subprocess.Popen(command0, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
        , shell=True) as proc:
   print(proc.stdout.read())

try:
    jsonFile = open(json_dir + "/pm2_jlist_status.json")
except IOError:
    print("ERROR: Opening file\n")
    raise SystemExit

data = json.load(jsonFile)
card_miners = []
for dataItem in data:

    try:
        args = dataItem["pm2_env"]["args"]

        #Calculate average Loss based on ~last 3hrs
        command1 =["tail -4200 /root/.pm2/logs/" + str(dataItem["name"]) + "-out.log | grep Loss: | cut -c 206-209 | awk '{ total += $1; count++ } END { print total/count }'"]
        with subprocess.Popen(command1, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
                , shell=True) as proc:
            avg_loss = str(proc.stdout.read())[0:5]
            avg_loss = avg_loss.replace("\n", "")
        
        #pm2 process data
        pm_name = str(dataItem["name"])
        pm_id = str(dataItem["pm_id"]) 
        pm_pid = str(dataItem["pid"]) 
        pm_status = str(dataItem["pm2_env"]["status"])
        pm_uptime_ts = datetime.fromtimestamp(int(dataItem["pm2_env"]["pm_uptime"])/1000)
        uptime = time_since_dttm(pm_uptime_ts)

        if AXON_ARG in args:
            axonInd = args.index(AXON_ARG)
            axon = str(dataItem["pm2_env"]["args"][axonInd+1])
        else:
            axon = str("NoAxon")

        if MODEL_ARG in args:
            modelInd = args.index(MODEL_ARG)
            model = str(dataItem["pm2_env"]["args"][modelInd+1])
        else:
            model = str("NoModel")

        if SUBTENS_ARG in args:
            subtensInd = args.index(SUBTENS_ARG)
            subtensor = str(dataItem["pm2_env"]["args"][subtensInd+1]).split(':', 1)[0]
        else:
            subtensor = str("nakamoto")

        my_miner = Miner(pm_name, pm_pid, pm_status, uptime, axon, model, subtensor, avg_loss, str(pm_uptime_ts) )
        card_miners.append( my_miner )

    except KeyError:
        pm_name = str(dataItem["name"])
        print(f"{pm_name} has no args")

# Display miner data
sorted_miners = []
sorted_miners = sorted(card_miners, key=lambda miner: miner.pm_uptime_ts)

print("[bold white]{}[/bold white]".format( "\n---------------------------------------------------".ljust(20) ) )
print( "[bold]{}{}{}{}{}{}{}{}[/bold]"
            .format("Miner".ljust(8),"PID".ljust(8), "Status".ljust(8), "Uptime".ljust(10), "Axon".ljust(7), "Subtensor".ljust(16), "AvLoss".ljust(7), "Model".ljust(30)) )
for miner in sorted_miners:
    if miner.pm_status == "online":
        print( "[bold blue]{}[/bold blue][grey]{}[/grey][green]{}[/green][grey]{}[/grey][grey]{}[/grey][grey]{}[/grey][yellow]{}[/yellow][blue]{}[/blue]"
            .format(miner.pm_name.ljust(8), miner.pm_pid.ljust(8), miner.pm_status.ljust(8), miner.uptime.ljust(10), miner.axon.ljust(7), miner.subtensor.ljust(16), miner.avg_loss.ljust(7), miner.model.ljust(30)) )
    else:
        print( "[bold blue]{}[/bold blue][grey]{}[/grey][red]{}[/red][grey]{}[/grey][grey]{}[/grey][grey]{}[/grey][yellow]{}[/yellow]"
            .format(miner.pm_name.ljust(8), miner.pm_pid.ljust(8), miner.pm_status.ljust(8), miner.uptime.ljust(10), miner.axon.ljust(7), miner.subtensor.ljust(16), miner.avg_loss.ljust(7), miner.model.ljust(30)) )

#Display GPU usage
print("[bold white]{}[/bold white]".format( "\n------------ GPU Usage: -----------------".ljust(20) ) )

cmd_gpu_chk = ['nvidia-smi']  
with subprocess.Popen(cmd_gpu_chk, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
        , shell=True) as proc:
    cmd_gpu_chk = proc.stdout.read()
#check for Failed to initialize NVML: Unknown Error
if cmd_gpu_chk.startswith('Failed'):
    print("[bold red]NVML: Unknown Error[/bold red]\n")
else:
    command2 = ['nvidia-smi | sed -n 10p && nvidia-smi -q | grep -e "GPU Memory"']
    with subprocess.Popen(command2, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
            , shell=True) as proc:
        print(proc.stdout.read())

print("[bold white]{}[/bold white]".format( "--------- Errors & Warnings: -----------".ljust(20) ) )
#Display pm2 error logs from last 3 days
for dataItem in data:
    print( "[bold blue]{}[/bold blue]".format( str(dataItem["name"]).ljust(10)  ) )
    command3 = ['tail -1 /root/.pm2/logs/' + str(dataItem["name"]) + '-error.log']
    with subprocess.Popen(command3, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
            , shell=True) as proc:
        cmd3_out = datetime.strptime(proc.stdout.read()[0:19],"%Y-%m-%dT%H:%M:%S")
    
    if cmd3_out >= datetime.today() - timedelta(days=2):
        print( "[bold red]{}[/bold red] {}".format( "Last errors: ", str(cmd3_out) ) )
        command4 = ['tail -7 /root/.pm2/logs/' + str(dataItem["name"]) + '-error.log | grep -Fv -e "Using pad_token" -e "config_info = json_normalize" -e "KeyboardInterrupt" -e "───────────" -e "json_normalize is deprecated" -e "�─╯ │"']
        with subprocess.Popen(command4, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
                , shell=True) as proc:
            cmd4_out = proc.stdout.read()
            print(cmd4_out)
    else: 
        print( "[green]Last errors older than [/green]" + str(cmd3_out))

#Display exceptions from pm2 standard logs
    command4 = ["tail -2000 /root/.pm2/logs/" + str(dataItem["name"]) + "-out.log | awk '/xception/ {$1=$19=$20=\"\"; print}' | sed -r \"s/\x1B\[([0-9]{1,3}((;[0-9]{1,3})*)?)?[m|K]//g\" | cut -c -160"]
    with subprocess.Popen(command4, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
            , shell=True) as proc:
        cmd4_out = proc.stdout.read()
        if(not cmd4_out):
            continue
        else:
            print("[bold red]{}[/bold red]".format( "Exceptions:" ) )
            print(cmd4_out)

jsonFile.close()