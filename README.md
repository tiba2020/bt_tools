# bt_tools

## Start:

`cd /workspace`

Sklonowanie repo:

`git clone https://github.com/tiba2020/bt_tools`

`cd bt_tools`

`pip3 install -r requirements.txt`

## Uruchomienie automatycznych notyfikacji:

W error_notif uzupelniamy swoj webhook kanalu discord: WEB_HOOK:

`sed -i -e 's,TWOJ_WEBHOOK_UZUPELNIC,TUTAJ_WKLEJ_SWOJ_WEBHOOK,g' error_notif.py`

Lub ręcznie edytując plik: `nano error_notif.py`

(opcja) w skrypcie ustawiamy nazwę karty jako stałą CARD_NAME

uruchomienie sesji TMUX: `tmux new -tmonit`

(opcja) na podzie ustawiamy zmienna srodowiskowa RUNPOD_POD_TBNM, np: `export RUNPOD_POD_TBNM="6000_01"`

Przejscie do katalogu bt_tools: `cd /workspace/bt_tools`

Uruchomienie skryptu: `python3 error_notif.py`

Wyjscie z sesji monitorujacej tmux: `ctrl + b -> d (command + b -> d)`

## Uruchomienie monitora minerow na podzie (bez notyfikacji - tylko bieżący podgląd):

`while true; do clear && python3 /workspace/bt_tools/pod_monit.py; sleep 300s; done`
