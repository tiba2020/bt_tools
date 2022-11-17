# bt_tools

## Start:

`cd /workspace`

Sklonowanie repo:
`git clone https://github.com/tiba2020/bt_tools`

`cd bt_tools`

`pip3 install -r requirements.txt`

(opcja) na podzie ustawiamy zmienna srodowiskowa RUNPOD_POD_TBNM, np: `export RUNPOD_POD_TBNM="6000_01"`

(opcja) w skrypcie ustawiamy nazwe karty jako stala CARD_NAME

## Uruchomienie automatycznych notyfikacji:

W error_notif uzupelniamy swoj webhook kanalu discord: WEB_HOOK:

`nano error_notif.py`

lub: `sed -i -e 's,WEB_HOOK,ZAMIEN_NA_SWOJ_WEBHOK,g' error_notif.py`

uruchomienie sesji TMUX: `tmux new -tmonit`

Przejscie do katalogu bt_tools: `cd /workspace/bt_tools`

Uruchomienie skryptu: `python3 error_notif.py`

Wyjscie z sesji monitorujacej `tmux: ctrl + d (command + d)`

## Uruchomienie monitora minerow na podzie:

`while true; do clear && python3 /workspace/bt_tools/pod_monit.py; sleep 120s; done`
