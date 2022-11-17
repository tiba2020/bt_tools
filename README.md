# bt_tools
Start
Sklonowanie repo:
git clone https://github.com/tiba2020/bt_tools


Skrypt error_notif.py: sprawdzajace bledy / wyjatki minerow i slacy notyfikacje na kanal discord

    Uruchomienie:
    1. uzupelniamy swoj webhook kanalu discord: WEB_HOOK
    2. instalacja: pip3 install discord_webhook && pip3 install rich && 
    3. uruchomienie sesji TMUX: tmux new -tmonit
    4. (opcja) na podzie ustawiamy zmienna srodowiskowa RUNPOD_POD_TBNM, np: export RUNPOD_POD_TBNM = "6000_01"
    5. (opcja) w skrypcie ustawiamy nazwe karty jako stala CARD_NAME
    6. Przejscie do katalogu bt_tools: cd /workspace/bt_tools
    6. Uruchomienie skryptu: python3 error_notif.py
    7. Wyjscie z sesji monitorujacej tmux: ctrl + d (command + d)
