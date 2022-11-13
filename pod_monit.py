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
       - error display
2022-11-01 tiba
"""
import json
import subprocess
from rich import print
from datetime import datetime, timedelta

MODEL_ARG = "--neuron.model_name"
SUBTENS_ARG = "--subtensor.chain_endpoint"
AXON_ARG = "--axon.port"


# prepare pm2 process data for parsing
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

    #Calculate average Loss based on ~last 3hrs
    command1 =["tail -1200 /root/.pm2/logs/" + str(dataItem["name"]) + "-out.log | grep Loss: | cut -c 206-209 | awk '{ total += $1; count++ } END { print total/count }'"]
    with subprocess.Popen(command1, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
            , shell=True) as proc:
        avg_loss = "AvgLoss:" + str(proc.stdout.read())[0:5]
        avg_loss = avg_loss.replace("\n", "")
    
    #pm2 process data
    pm_name = str(dataItem["name"])
    pm_id = str(dataItem["pm_id"]) 
    pm_pid = str(dataItem["pid"]) 
    pm_status = str(dataItem["pm2_env"]["status"])
    pm_uptime_ts = datetime.fromtimestamp(int(dataItem["pm2_env"]["pm_uptime"])/1000)
    uptime = str(datetime.today() - pm_uptime_ts).split('.', 1)[0]

    infoString = ""
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
        subtensor = str(dataItem["pm2_env"]["args"][subtensInd+1])
    else:
        subtensor = str("nakamoto")

    #Formatting and display
    if pm_status == "online":
        print( "[bold blue]{}[/bold blue][grey]{}[/grey][grey]{}[/grey][green]{}[/green][grey]{}[/grey][grey]{}[/grey][grey]{}[/grey][yellow]{}[/yellow][blue]{}[/blue]"
            .format(pm_name.ljust(10), pm_id.ljust(3), pm_pid.ljust(8), pm_status.ljust(8), uptime.ljust(9), axon.ljust(6), subtensor.ljust(21), avg_loss.ljust(14), model.ljust(30)) )
    else:
        print( "[bold blue]{}[/bold blue][grey]{}[/grey][grey]{}[/grey][red]{}[/red][grey]{}[/grey][grey]{}[/grey][grey]{}[/grey][yellow]{}[/yellow]"
            .format(pm_name.ljust(10), pm_id.ljust(3), pm_pid.ljust(8), pm_status.ljust(8), uptime.ljust(9), axon.ljust(6), subtensor.ljust(21), avg_loss.ljust(14), model.ljust(30)) )

#Display GPU usage
print("[bold white]{}[/bold white]".format( "\nGPU Usage:".ljust(20) ) )


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

#Display exceptions from pm2 standard logs tail -2000 /root/.pm2/logs/miner36-out.log
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