import xbmc
import xbmcgui
import xbmcplugin
import xbmcvfs
import json
import os
import sys

ADDON_ID = 'plugin.video.acestream_manager'
ADDON_PATH = xbmcvfs.translatePath(f'special://profile/addon_data/{ADDON_ID}')
JSON_FILE = os.path.join(ADDON_PATH, 'links.json')

if not os.path.exists(ADDON_PATH):
    os.makedirs(ADDON_PATH)

def load_links():
    if os.path.exists(JSON_FILE):
        try:
            with open(JSON_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list) and all(isinstance(i, dict) for i in data):
                    return data
        except json.JSONDecodeError:
            pass  # Se il file è corrotto, lo resetta

    return []  # Ritorna una lista vuota se il file è corrotto o inesistente


def save_links(links):
    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(links, f, indent=4)

def add_link():
    # Chiedi l'URL Acestream
    keyboard = xbmc.Keyboard('', 'Inserisci il link Acestream')
    keyboard.doModal()
    if not keyboard.isConfirmed():
        return
    link = keyboard.getText().strip()
    if not link:
        xbmcgui.Dialog().ok('Errore', 'Nessun link inserito.')
        return

    # Chiedi il nome del link
    keyboard = xbmc.Keyboard('', 'Inserisci il nome del link')
    keyboard.doModal()
    if not keyboard.isConfirmed():
        return
    name = keyboard.getText().strip()
    if not name:
        name = f'Link {len(load_links()) + 1}'  # Nome predefinito

    # Salva il link con il nome
    links = load_links()
    links.append({"name": name, "url": link})
    save_links(links)
    
    xbmcgui.Dialog().ok('Acestream Manager', 'Link aggiunto con successo!')
    main_menu()  # Ritorna al menu principale

def list_links():
    links = load_links()
    if not links:
        xbmcgui.Dialog().ok('Acestream Manager', 'Nessun link disponibile.')
        return

    menu_items = []
    for index, item in enumerate(links):
        name = item["name"]
        acestream_url = item["url"]

        # Horus utilizza il formato: plugin://plugin.video.horus/?url=<acestream_url>
        horus_url = f'plugin://script.module.horus/?action=play&url={acestream_url}'

        li = xbmcgui.ListItem(name)
        li.setInfo('video', {'title': name})
        li.setProperty('IsPlayable', 'true')

        menu_items.append((horus_url, li, False))

    xbmcplugin.addDirectoryItems(int(sys.argv[1]), menu_items, len(menu_items))
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

def remove_link():
    links = load_links()
    if not links:
        xbmcgui.Dialog().ok('Acestream Manager', 'Nessun link disponibile da eliminare.')
        return

    choices = [f'{item["name"]}' for item in links]
    selected = xbmcgui.Dialog().select('Seleziona un link da eliminare', choices)
    if selected != -1:
        del links[selected]
        save_links(links)
        xbmcgui.Dialog().ok('Acestream Manager', 'Link eliminato con successo!')
        main_menu()  # Ritorna al menu principale

def main_menu():
    options = ['Aggiungi Link', 'Visualizza Link', 'Elimina Link']
    selected = xbmcgui.Dialog().select('Acestream Manager', options)
    if selected == 0:
        add_link()
    elif selected == 1:
        list_links()
    elif selected == 2:
        remove_link()

if __name__ == '__main__':
    main_menu()
