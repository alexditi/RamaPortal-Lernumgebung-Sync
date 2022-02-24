import datetime
import requests
import os
import json
import shutil
import subprocess
import sys
import unicodedata
from bs4 import BeautifulSoup
from queue import LifoQueue
from tkinter import *
from tkinter import messagebox, filedialog
from time import sleep


# tooltip class
class ToolTip(object):
    """
    ToolTip Klasse: Zeigt neben einem Tkinter Widget einen Text an, wenn man über dieses mit dem Zeiger fährt.
    """

    def __init__(self, widget: BaseWidget, text: str) -> None:
        """
        ToolTip Klasse: Zeigt neben dem Tkinter Widget einen Text an, wenn man über das Widget mit dem Mauszeiger
        fährt.

        :param widget: Parent Widget des Tooltips, für das der Tooltip angezeigt wird.
        :param text: Der anzuzeigende Text.
        """

        self.text = text
        self.widget = widget
        self.tipwindow = None
        self.x = self.y = 0
        self.widget.bind("<Enter>", self._showtip)
        self.widget.bind("<Leave>", self._hidetip)

    def _showtip(self, _event: Event) -> None:
        if self.tipwindow or not self.text:
            return
        x = self.widget.winfo_rootx() + 37
        y = self.widget.winfo_rooty() + 27
        self.tipwindow = tw = Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = Label(tw, text=self.text, justify=LEFT, background=bg_color, foreground=font_color, relief=SOLID, borderwidth=1, font="Helvetia 8")
        label.pack(ipadx=1)

    def _hidetip(self, _event: Event) -> None:
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()


# custom DropdownDialog class with Dropdown menu
class DropdownDialog(object):
    """
    Custom DropdownDialog. Es wird ein Dialog angezeigt mit einem Dropdown Menu, aus dem eine Option ausgewählt
    werden kann.
    """

    def __init__(self, _root: Tk, msg: str, selection: StringVar, selection_list: list = None):
        """
        Custom DropdownDialog: Es wird ein Dialog mit Dropdown Menu angezeigt, aus dem eine Option ausgewählt werden
        kann. Die Auswahl wird in der dem Konstruktor übergebenen Tkinter Variable gespeichert und kann nach der
        Bestätigung des Dialogs von root window ausgelesen werden. Erscheint der Dialog, wird der Fokus vom root window
        genommen, es können keine Buttons mehr gedrückt werden und es wird gewartet, bis der Dialog geschlossen wird.

        :param _root: root window, also die Tk Instanz, für die der Dialog angezeigt werden soll
        :param msg: Die anzuzeigende Message auf dem Dialog
        :param selection: Tkinter StringVar, in der die Selection nach dem Submit gespeichert wird
        :param selection_list: Liste an Auswahlmöglichkeiten
        """

        self.root = _root

        self.top = Toplevel(_root)
        self.top.protocol("WM_DELETE_WINDOW", self.cancel)

        self.selection = selection

        self.close_var = BooleanVar()
        self.close_var.set(FALSE)

        dialog_frame = Frame(self.top, borderwidth=4, relief='ridge')
        dialog_frame.pack(fill='both', expand=True)

        message_box = Message(dialog_frame, text=msg, width=250)
        message_box.pack(padx=4, pady=4)

        if selection_list is not None:
            self.selection.set(selection_list[0])

            option_menu = OptionMenu(dialog_frame, self.selection, *selection_list)
            option_menu.config(width=20, font="Helvetia 12")
            option_menu.pack(side=TOP)

            submit_btn = Button(dialog_frame, text="OK", command=self.submit, width=9)
            submit_btn.pack(padx=30, pady=4, side=LEFT)

        cancel_btn = Button(dialog_frame, text='Abbrechen', command=self.cancel)
        cancel_btn.pack(padx=30, pady=4, side=RIGHT)

        self.top.grab_set()
        self.root.wait_variable(self.close_var)

    def submit(self):
        self.close_var.set(TRUE)
        self.top.destroy()

    def cancel(self):
        self.selection.set("None")
        self.submit()


class TaskSchedulerDropdownDialog(object):
    """
    Dialog zur Auswahl, wie die Aufgabe für den Task Scheduler erstellt werden soll.
    """

    def __init__(self, _root: Tk, selection: StringVar, network_name: StringVar, options: list):
        """
        Über diesen Dropdown Dialog kann ausgewählt werden, wie die Aufgabe für den TaskScheduler erstellt wird.

        :param _root: root window, also die Tk Instanz, für die der Dialog angezeigt werden soll
        :param selection: Tkinter StringVar, in der die Selection nach dem Submit gespeichert wird
        :param network_name: Tkinter StringVar, in der der Name des Netzwerks gespeichert wird
        """

        self.root = _root

        self.top = Toplevel(_root)
        self.top.protocol("WM_DELETE_WINDOW", self.cancel)

        self.selection = selection
        self.selection.trace_add("write", self.show_network_name_entry)

        self.network_name = network_name

        self.close_var = BooleanVar()
        self.close_var.set(FALSE)

        dialog_frame = Frame(self.top, borderwidth=4, relief='ridge')
        dialog_frame.pack(fill='both', expand=True)

        msg = "Die Lernumgebung Synchronisation kann automatisch nach der Benutzeranmeldung gestartet werden, wenn eine " \
              "bestimme Netzwerkverbindung vorhanden ist. Dazu wird am besten das Heimnetzwerk ausgewählt, sodass die " \
              "Synchronisation gestartet wird, wenn man den PC zu Hause startet.\nDie erste Option richtet den Autostart " \
              "ein mit dem aktuell verbundenen Netzwerk als Bedingung.\nDie zweite Option richtet den Autostart ein mit " \
              "einem bestimmten Netzwerk, dessen Name angegeben werden muss.\nAußerdem kann der Autostart deaktiviert " \
              "werden mit der dritten Option."
        message_box = Message(dialog_frame, text=msg, width=420)
        message_box.pack(padx=4, pady=4)

        network_name_frame = Frame(dialog_frame, width=420, height=20)
        network_name_frame.pack()

        self.network_name_label = Label(network_name_frame, text="Netzwerk Name: ")
        self.network_name_label.pack(side=LEFT)

        self.network_name_entry = Entry(network_name_frame, textvariable=self.network_name, width=20)
        self.network_name_entry.pack(side=RIGHT)

        self.selection_list = options

        self.selection.set(self.selection_list[0])
        option_menu = OptionMenu(dialog_frame, self.selection, *self.selection_list)
        option_menu.config(width=40, font="Helvetia 12")
        option_menu.pack(side=TOP)

        submit_btn = Button(dialog_frame, text="OK", command=self.submit, width=9)
        submit_btn.pack(padx=30, pady=4, side=LEFT)

        cancel_btn = Button(dialog_frame, text='Abbrechen', command=self.cancel)
        cancel_btn.pack(padx=30, pady=4, side=RIGHT)

        self.top.grab_set()
        self.root.wait_variable(self.close_var)

    def show_network_name_entry(self, _array, _index, _mode):
        if self.selection.get() == self.selection_list[1]:
            self.network_name_entry.pack(side=RIGHT)
            self.network_name_label.pack(side=LEFT)
        else:
            self.network_name_entry.pack_forget()
            self.network_name_label.pack_forget()

    def submit(self):
        self.close_var.set(TRUE)
        self.top.destroy()

    def cancel(self):
        self.selection.set("None")
        self.submit()


# frozen executable check
frozen = getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")

# initialize Tkinter root
root = Tk()
root.wm_title("LU Synchronisation")
root.wm_minsize(300, 330)
root.wm_maxsize(300, 330)
root.withdraw()

# get icon file and apply it to the root window
if frozen:
    base_path = f"{sys._MEIPASS}\\"
else:
    base_path = ""
root.iconbitmap(os.path.join(base_path, "logo_rama.ico"))

# some global variables
tmpdir = f"{os.environ.get('localappdata')}\\RamaPortal Client"
url = "https://portal.rama-mainz.de"
s = requests.Session()
error_log = []
userdata = {}
LU_dir = ""
show_password = False
delete_before_sync = BooleanVar()
sync_only_new = BooleanVar()
sync_only_new.set(TRUE)
previous_dir = ""

version = "v7.0"

# color constants
bg_color = "#282828"
font_color = "light grey"
rama_color = "#A51320"
rama_color_active = "#9E1220"


def check_login() -> bool:
    """
    Diese Methode überprüft die aktuellen Anmeldedaten.

    :return: True, wenn die Anmeldung mit den aktuellen Benutzerdaten erfolgreich war, andernfalls False
    """

    return not (BeautifulSoup(s.post(f"{url}/index.php", {"username": userdata.get("username"), "password": userdata.get(
            "password")}).text, features="html.parser").text.find("angemeldet als") == -1)


def launch_updater() -> None:
    """
    Das Updater Script wird heruntergeladen und ausgeführt. Als Argumente werden der Pfad zum alten LU Sync Script und
    die neueste Version übergeben, die neueste Version wird dem UpdateLog entnommen. Der Updater wird als eigenständiger
    subprocess gestartet und der LU Sync Script wird beendet.

    :return: None
    """

    # download updater
    with open(f"{tmpdir}/LU_updater.exe", "wb+") as updater:
        updater.write(requests.get(f"https://github.com/alexditi/RamaPortal-Lernumgebung-Sync/raw/{updateLog.get('version')}/Lernumgebung Sync/LU_updater.exe").content)

    # start updater
    if frozen:
        running_file_path = sys.executable
    else:
        running_file_path = os.path.abspath(__file__).replace("\\", "/").replace(".pyw", ".exe").replace(".py", ".exe")
    subprocess.Popen([f"{tmpdir}/LU_updater.exe", running_file_path, updateLog.get("version")], shell=False, stdin=None,
                     stdout=None, stderr=None, close_fds=True, creationflags=subprocess.DETACHED_PROCESS)
    sleep(1)
    root.destroy()
    sys.exit(0)


def insert_dir() -> None:
    """
    Diese Methode wird aufgerufen, wenn der Button neben dem Entry Label für den Synchronisationspfad gedrückt wird.
    Der Filedialog wird geöffnet und sein return wird dem Entry Label übergeben.

    :return: None
    """
    path = filedialog.askdirectory()
    if path:
        dir_entry.delete(0, END)
        dir_entry.insert(0, path)


def show_settings() -> None:
    """
    Diese Methode wird aufgerufen, wenn der Button Einstellungen gedrückt wird, damit der Einstellungen Tab angezeigt
    wird. Wenn die Einstellungen beim Starten der LU Sync gezeigt werden müssen, falls die userdata.json Datei nicht
    existiert, beschädigt ist oder die Anmeldedaten falsch sind, wird der Tab direkt von dort gezeigt, nicht über diese
    Methode.

    :return: None
    """

    global previous_dir

    # hide main frame
    main_frame.pack_forget()

    # clear userdata entries
    username_entry.delete(0, END)
    password_entry.delete(0, END)
    dir_entry.delete(0, END)

    username_entry.insert(0, userdata.get("username"))
    password_entry.insert(0, userdata.get("password"))
    dir_entry.insert(0, userdata.get("dir"))

    # save previous LU Sync dir
    previous_dir = LU_dir

    userdata_frame.pack(expand=True, fill=BOTH)


def submit_settings() -> None:
    """
    Diese Methode wird aufgerufen, wenn der "Speichern" Button im Einstellungen Tab gedrückt wird, um die eingegebenen
    Benutzerdaten zu speichern. Es wird auf die Korrektheit der Anmeldedaten überprüft, die Benutzerdaten werden in der
    userdata.json Datei gespeichert und, falls der Synchronisationspfad geändert wurde, werden die Dateien verschoben
    und je nach Auswahl der alte Ordner gelöscht.

    :return: None
    """

    global userdata, LU_dir

    # create userdata dict
    userdata = {"username": username_entry.get(), "password": password_entry.get(), "dir": dir_entry.get()}

    LU_dir = f"{userdata.get('dir')}/Lernumgebung OfflineSync"

    # write userdata to the userdata file
    with open(f"{tmpdir}/userdata_LU.json", "w+") as userdata_creator:
        json.dump(userdata, userdata_creator)

    # make sure the last user is logged out in order to check for the new userdata
    if check_login():
        s.get(f"{url}/index.php?abmelden=1")

    # check new userdata
    if not check_login():
        # wrong login data, clear login entries and show error message
        username_entry.delete(0, END)
        password_entry.delete(0, END)
        messagebox.showerror("Anmeldung fehlgeschlagen!", "Falscher Benutzername oder falsches Passwort")
        return

    # correct userdata, check for changed LU Sync directory
    if previous_dir and LU_dir != previous_dir and os.path.exists(previous_dir):
        options = ["Dateien verschieben", "Dateien Kopieren", "Keine Dateien in den neuen Ordner kopieren/verschieben"]
        selected_action = StringVar()
        DropdownDialog(root, "Der Synchronisationspfad wurde geändert. Wähle eine der folgenden Optionen aus, was mit "
                             "den Dateien im alten Ordner gemacht werden soll. Es werden nur die Hauptordner verschoben"
                             "oder kopiert, die in der Lernumgebung sind.", selected_action, options)

        if selected_action.get() == options[0]:
            # move files
            try:
                for group in get_groups():
                    shutil.move(f"{previous_dir}/{group[1]}", f"{LU_dir}/{group[1]}")
                if len(os.listdir(previous_dir)) == 0:
                    shutil.rmtree(previous_dir)
            except FileNotFoundError:
                messagebox.showerror("Fehler beim Verschieben",
                                     "Die Dateien konnten nicht verschoben werden, weil der alte Ordner nicht mehr existiert.")
            except PermissionError:
                print("Couldn't delete the previous directory due to Permission restrictions")
        elif selected_action.get() == options[1]:
            # copy files
            try:
                for group in get_groups():
                    shutil.copytree(f"{previous_dir}/{group[1]}", f"{LU_dir}/{group[1]}")
            except FileNotFoundError:
                messagebox.showerror("Fehler beim Verschieben",
                                     "Die Dateien konnten nicht verschoben werden, weil der alte Ordner nicht mehr existiert.")
        elif selected_action.get() == options[2]:
            # don't move any files
            pass
        elif selected_action.get() == "None":
            return

    userdata_frame.pack_forget()
    main_frame.pack(expand=True, fill=BOTH)


def toggle_show_password() -> None:
    """
    Schaltet zwischen dem versteckten Passwort (*) und dem sichtbaren Passwort um.

    :return: None
    """

    global show_password
    if show_password:
        password_entry.config(show="*")
    else:
        password_entry.config(show="")
    show_password = not show_password


def mk_dir(path: str) -> None:
    """
    Erstellt ein Verzeichnispfad und fängt etwaige Exceptions auf

    :param path: Das zu erstellende Verzeichnis
    :return:
    """

    global error_log
    try:
        try:
            os.mkdir(path)
        except FileExistsError:
            pass
    except Exception as ex:
        error_log.append(("Folgender Pfad konnte nicht erstellt werden: ", ex, path))


def download_file(file: dict, dir_string: str) -> None:
    """
    Lädt eine gegebene Datei, die über ihre ID identifiziert wird, herunter. Die Funktion parsed den Dateityp aus der
    Lernumgebung in einen gängigen Dateityp um. Außerdem wird für einige Dateien ein Wrapper benötigt, in dem der Inhalt
    der Datei eingebettet wird, z.B. Internetlinks oder Text Dateien, die als html Datei gespeichert sind.

    :param file: Dictionary mit den Informationen "id", "name" und "typ"
    :param dir_string: Pfad unter dem die Datei gespeichert werden soll
    :return: None
    """

    ext = file.get("typ")
    wrapper = b"file_content"
    if ext == "handschriftl Notiz":
        # not yet implemented
        pass
    elif ext == "tabellenkalkulation":
        # not yet implemented
        pass
    elif ext == "lnk":
        ext = ".url"
        wrapper = b"[{000214A0-0000-0000-C000-000000000046}]\nProp3=19,11\n[InternetShortcut]\nIDList=\nURL=file_content"
    elif ext == "ytb":
        ext = ".url"
        wrapper = b"[{000214A0-0000-0000-C000-000000000046}]\nProp3=19,11\n[InternetShortcut]\nIDList=\nURL=https://www.youtube.com/watch?v=file_content"
    elif ext == "img":
        ext = ".jpg"
    elif ext == "aud":
        ext = ".mp3"
    elif ext == "vid":
        ext = ".mp4"
    elif ext == "download":
        ext = ""
    elif ext == "html":
        ext = ".html"
        wrapper = b"<head><style>body {font-family: Arial;}</style></head><body>file_content</body>"
    elif ext == "Test":
        # not yet implemented
        pass
    elif ext == "PhET simulation":
        # not yet implemented
        pass
    else:
        ext = "." + ext

    if sync_only_new.get() and os.path.exists(dir_string + "/" + file.get("name") + ext):
        return

    global error_log
    print(f"Downloading File {file.get('name')} to {dir_string}/{file.get('name')}{ext}")

    with open(f"{dir_string}/{file.get('name')}{ext}", "wb+") as s_file:
        # noinspection PyBroadException
        try:
            resp = s.get(f"{url}/edu/edufile.php?id={file.get('id')}&download=1")
            s_file.write(wrapper.replace(b"file_content", resp.content))
        except Exception as ex:
            error_log.append(("Beim speichern der folgenden Datei ist ein Fehler aufgetreten: ", ex, file))


def get_groups() -> list:
    """
    List alle Fächer / Überordner as der Lernumgebung aus, damit so die Grundstruktur für das Verzeichnis steht.

    :return: groupList. Eine List mit Tupeln nach dem Muster (group_id, group_name)
    """
    a_list = BeautifulSoup(s.get(url + "/edu/edumain.php").text, features="html.parser").find(class_="flist").find_all(name="a")

    return [(a.get("href")[a.get("href").find("gruppe=") + 7: a.get("href").find("§ion=")], a.get("title")) for a in a_list]


def get_material_list(href: str) -> dict:
    """
    Lädt die material_list eines bestimmten LU Ordners in ein Dictionary. Die material_list wird als json Objekt
    verarbeitet.

    :param href: Link des LU Ordners, dessen material_list geladen werden soll.
    :return:
    """
    material_script = BeautifulSoup(s.get(href).text, features="html.parser").find(class_="hstack").find_all(name="script")[::-1][0]

    return json.loads(str(material_script).replace("<script>window.materialListe = ", "").replace(";</script>", ""))


def syncLU() -> None:
    """
    Methode zum Herunterladen der LU. Dabei werden die Hauptordner (Fächer) nacheinander abgearbeitet. Innerhalb der
    Hauptordner wird jeder Unterordner geöffnet; der Zustand des vorherigen Ordners wird auf einen Stack abgelegt. Ist
    das Ende eines Ordners erreicht worden, geht die Methode zum vorherigen Ordner zurück, ist es eine Datei, wird diese
    heruntergeladen.

    :return: None
    """

    global error_log
    error_log = []

    settings_btn.config(state=DISABLED)
    sync_btn.config(state=DISABLED)
    delete_cb.config(state=DISABLED)
    sync_new_cb.config(state=DISABLED)

    if delete_before_sync.get() and messagebox.askyesno("Ordner löschen?", 'Es werden alle Ordner für Fächer der LU komplett gelöscht, auch eigene Dateien in diesen Ordnern!'):
        try:
            info_label.config(text="Lösche alte Ordner")
            root.update()
            for group in get_groups():
                shutil.rmtree(f"{LU_dir}/{group[1]}")
        except FileNotFoundError:
            pass

    try:
        # get groups
        groupList = get_groups()

        # get each group's file directory
        dir_stack = LifoQueue()
        mk_dir(LU_dir)

        for group in groupList:
            for sect, dir_sa in [("publ", "Öffentlich"), ("priv", "Privat")]:
                print(group[1], group[0], dir_sa)
                progress_label.config(text=f"{group[1]} ({groupList.index(group)}/{len(groupList)})")
                root.update()

                # access main directory, create folder
                current_material_list = get_material_list(url + "/edu/edumain.php?gruppe=" + group[0] + "&section=" + sect)
                dir_string = LU_dir + "/" + group[1]
                mk_dir(dir_string)
                dir_string += "/" + dir_sa
                mk_dir(dir_string)

                n = 0
                while True:
                    try:
                        # update current_file
                        dir_stack.put((current_material_list, n))
                        current_file = current_material_list[n]

                        # parsing key "name" to conform w10 path decoding
                        file_name = current_file.get("name").replace("/", " ").replace("\\", "").replace(
                            ":", " ").replace("*", " ").replace("?", " ").replace('"', " ").replace("<", " ").replace(
                            ">", "").replace("|", "").replace("&amp;", "&").replace("&quot;", ' ').replace(
                            "&apos;", "'").replace("&lt;", "").replace("&gt;", " ")
                        while file_name[len(file_name) - 1] == " ":
                            file_name = file_name[:-1]
                        current_file.update({"name": file_name})
                        print(current_file.get("name"))

                        if current_file.get("typ") == "dir":
                            # directory
                            dir_string += "/" + current_file.get("name")
                            mk_dir(dir_string)
                            current_material_list = get_material_list(f"{url}/edu/edumain.php?gruppe={group[0]}&section={sect}&dir={current_file.get('id')}")
                            n = 0
                            print("changed dir to", current_file.get("name"))
                            info_label.config(text=current_file.get("name"))
                            root.update()
                        elif current_file.get("typ") == "diropen":
                            pass
                        else:
                            # file
                            dir_stack.get()
                            info_label.config(text=current_file.get("name"))
                            root.update()
                            download_file(current_file, dir_string)
                    except IndexError:
                        # end of current materialList
                        dir_stack.get()

                        # return to prev directory
                        if not dir_stack.empty():
                            dir_string = dir_string[:-(dir_string[::-1].find("/") + 1)]
                            current_material_list, n = dir_stack.get()
                        # end of main directory
                        else:
                            break
                    n += 1

    except Exception as ex:
        error_log.append(("Anderweitige Fehlermeldung: ", ex, str(ex.__traceback__)))

    # delete error_log.txt if present (from previous versions) and only create the file if any errors occurred
    print("Finished with", len(error_log), "errors")
    if os.path.exists(f"{LU_dir}/ErrorLog.txt"):
        os.remove(f"{LU_dir}/ErrorLog.txt")
    if len(error_log) > 0:
        with open(f"{LU_dir}/ErrorLog.txt", "w+") as error_log_file:
            error_log_file.write("\n".join([str(error) for error in error_log]))

    # show final message an release buttons
    progress_label.config(text="Fertig!")
    e_msg = "Synchronisation erfolgreich abgeschlossen."
    if len(error_log) > 0:
        e_msg = f"Synchronisation mit {len(error_log)} Fehlern abgeschlossen. Siehe ErrorLog.txt für weitere Informationen."
    info_label.config(text=e_msg)
    settings_btn.config(state=NORMAL)
    sync_btn.config(state=NORMAL)
    delete_cb.config(state=NORMAL)
    sync_new_cb.config(state=NORMAL)


def register_task_template(network_name: str = "") -> None:
    """
    Diese Methode registriert eine Aufgabe in der Aufgabenplanung, die die LU Sync bei Anmeldung eines Benutzers und
    vorhandener Internetverbindung (bestimmtes Netzwerk, z.B. Heimnetzwerk) startet. Es werden die notwendigen
    Informationen über cmd bzw powershell Befehle eingeholt und dann eine xml Datei erstellt, die über einen powershell
    command als Aufgabe registriert wird.

    :param network_name: Name des Netzwerks, mit dem man verbunden sein muss, damit die LU Sync gestartet wird. Falls
    nicht spezifiziert, wird das aktuell verbundene Netzwerk verwendet.
    :return: None
    """
    # get username
    username = os.environ.get("username") or os.environ.get("user")

    # get date and time
    d = datetime.datetime.today()
    date_time = f"{d.year}-{str(d.month).zfill(2)}-{str(d.day).zfill(2)}T{str(d.hour).zfill(2)}:{str(d.minute).zfill(2)}:{str(d.second).zfill(2)}.{str(d.microsecond).zfill(6)}0"

    # get user sid
    user_sid = "".join(
        c for c in
        subprocess.run(["wmic", "useraccount", "where", f"name='{username}'", "get", "sid"], capture_output=True, text=True).stdout
        if unicodedata.category(c)[0] != "C" and c != " "
    ).replace("SID", "")

    # get name of current network
    # based on a powershell script, for reference see get_network_name.ps1
    # the reference script is not downloaded and executed, since powershell script execution is restricted
    # instead, only single commands are executed as they are not restricted
    if not network_name:
        default_ipv4_index = "".join(
            c for c in
            subprocess.run('powershell -command "Get-NetRoute -DestinationPrefix 0.0.0.0/0|Sort-Object {$_.RouteMetric+(Get-NetIPInterface -AssociatedRoute $_).InterfaceMetric}|Select-Object -First 1 -ExpandProperty InterfaceIndex"',
                           capture_output=True, text=True).stdout
            if unicodedata.category(c)[0] != "C" and c != " "
        )
        network_name = "".join(
            c for c in
            subprocess.run(f'powershell -command "(Get-NetConnectionProfile -InterfaceIndex {default_ipv4_index}).Name"',
                           capture_output=True, text=True).stdout
            if unicodedata.category(c)[0] != "C"
        )

    # get network guid
    # create get_guid script, for reference see file get_guid.cmd
    with open(f"{tmpdir}/get_guid.bat", "w+") as cmdlet:
        cmdlet.write(
            "@ECHO OFF\n"
            f"SET SearchString=\"\'Name\'^^^>{network_name}\"\n"
            "FOR /f \"delims=\" %%i IN (\'wevtutil qe Microsoft-Windows-NetworkProfile/Operational /q:\"Event[System[EventID=10000]]\" /c:100 /rd:true /f:xml ^| FINDSTR /R \"%SearchString%\"\') DO (\n"
            "ECHO %%i\n"
            ")"
        )
    # execute script and parse xml output
    network_guid = BeautifulSoup(
        subprocess.run([f"{tmpdir}/get_guid.bat"], capture_output=True, text=True).stdout, features="xml"
    ).find_all(Name="Guid")[0].text

    # get executable path
    if frozen:
        executable_path = sys.executable
    else:
        executable_path = os.path.abspath(__file__).replace("\\", "/").replace(".pyw", ".exe")

    print(username, date_time, user_sid, network_name, network_guid, executable_path)

    # create xml task scheduler file
    task_template = requests.get("https://raw.githubusercontent.com/alexditi/RamaPortal-Lernumgebung-Sync/master/Aufgabenplanung%20Vorlage/LU%20Sync.xml").content.decode("utf-16")
    task_template = task_template.replace("date_time", date_time)
    task_template = task_template.replace("username", username)
    task_template = task_template.replace("user_sid", user_sid)
    task_template = task_template.replace("network_name", network_name)
    task_template = task_template.replace("network_guid", network_guid)
    task_template = task_template.replace("executable_path", executable_path)

    with open(f"{tmpdir}/LU Sync.xml", "wb+") as file:
        file.write(task_template.encode("utf-16"))

    # register task
    res = subprocess.run(
        f"Powershell -Command \"Start-Process -FilePath \'powershell\' -ArgumentList \'-Command \"\"Register-ScheduledTask -TaskName \'\'LU Sync\'\' -Xml (Get-Content \'\'{tmpdir}\\LU Sync.xml\'\' | Out-String)\"\"\' -Verb RunAs\"",
        capture_output=True, text=True
    ).stdout
    print(res)


def show_task_settings() -> None:
    options = ["Aufgabe mit verbundenem Netzwerk erstellen", "Aufgabe mit Netzwerkname erstellen", "Aufgabe löschen"]
    selected_action = StringVar()
    network_name = StringVar()
    TaskSchedulerDropdownDialog(root, selected_action, network_name, options)

    if selected_action.get() == options[0]:
        # use connected network
        register_task_template()
    elif selected_action.get() == options[1]:
        # use given network name
        pass
    elif selected_action.get() == options[2]:
        # delete task
        pass


# check for available internet connection
v = None
try:
    v = requests.get("https://raw.githubusercontent.com/alexditi/RamaPortal-Lernumgebung-Sync/master/Lernumgebung%20Sync/updateLog.json", timeout=5)
except (requests.ConnectionError, requests.Timeout):
    messagebox.showwarning("Keine Internetverbindung!", "Stelle sicher, dass du eine Internetverbindung hast und starte die App erneut.")
    try:
        v = requests.get("https://raw.githubusercontent.com/alexditi/RamaPortal-Lernumgebung-Sync/master/Lernumgebung%20Sync/updateLog.json", timeout=5)
    except (requests.ConnectionError, requests.Timeout):
        sys.exit(0)

root.deiconify()

# main Frame
main_frame = Frame(root, bg=bg_color)
settings_btn = Button(main_frame, bg=rama_color, activebackground=rama_color_active, fg=font_color, activeforeground=font_color, text="Einstellungen", font="Helvetia 16 bold", command=show_settings, relief=FLAT)
settings_btn.pack(anchor=S, fill=X, pady=10, padx=8)
sync_btn = Button(main_frame, bg=rama_color, activebackground=rama_color_active, fg=font_color, activeforeground=font_color, text="Starte Synchronisation", font="Helvetia 16 bold", command=syncLU, relief=FLAT)
sync_btn.pack(anchor=S, fill=X, pady=10, padx=8)
cb_frame = Frame(main_frame)
delete_cb = Checkbutton(cb_frame, bg=bg_color, activebackground=bg_color, variable=delete_before_sync)
delete_cb.pack(side=LEFT)
Label(cb_frame, text="Ordner vor Update löschen", font="Helvetia 12", fg=font_color, bg=bg_color).pack(side=RIGHT, fill=Y)
cb_frame.pack(pady=5, padx=8, anchor=W, side=TOP)
cb_frame1 = Frame(main_frame)
sync_new_cb = Checkbutton(cb_frame1, bg=bg_color, activebackground=bg_color, variable=sync_only_new)
sync_new_cb.pack(side=LEFT, anchor=S)
Label(cb_frame1, text="Nur neue Dateien synchronisieren", font="Helvetia 12", fg=font_color, bg=bg_color).pack(side=RIGHT, fill=Y)
cb_frame1.pack(pady=5, padx=8, anchor=W, side=TOP)
sync_frame = Frame(main_frame, bg=rama_color, width=250, height=150)
sync_frame.pack_propagate(False)
progress_label = Label(sync_frame, bg=bg_color, fg=font_color, font="Helvetia 14 bold", text="")
progress_label.pack(fill=X)
info_label = Message(sync_frame, bg=bg_color, fg=font_color, font="Helvetia 10", text="", aspect=400)
info_label.pack(fill=BOTH, expand=True)
sync_frame.pack(side=TOP, pady=5)

# userdata Frame
userdata_frame = Frame(root, bg=bg_color)
Label(userdata_frame, bg=bg_color, fg=font_color, text="Benutzername", font="Helvetia 16 bold").pack(fill=X, anchor=N, pady=5)
username_entry = Entry(userdata_frame, bg=bg_color, fg=font_color, font="Helvetia 16", relief=FLAT, highlightthickness=2, highlightcolor="black", highlightbackground="black")
username_entry.pack(fill=X, anchor=N, padx=8)
Label(userdata_frame, bg=bg_color, fg=font_color, text="Passwort", font="Helvetia 16 bold").pack(fill=X, anchor=N, pady=5)
password_frame = Frame(userdata_frame, bg=bg_color)
password_entry = Entry(password_frame, bg=bg_color, fg=font_color, font="Helvetia 16", show="*", relief=FLAT, highlightthickness=2, highlightcolor="black", highlightbackground="black")
show_password_btn = Button(password_frame, text="O", font="Helveita 16 bold", bg=bg_color, activebackground=bg_color, fg=rama_color, activeforeground=rama_color_active, relief=FLAT, width=2, command=toggle_show_password)
ToolTip(show_password_btn, "Passwort anzeigen")
show_password_btn.pack(side=RIGHT)
password_entry.pack(fill=X, side=LEFT)
password_frame.pack(fill=X, anchor=N, padx=8)
Label(userdata_frame, bg=bg_color, fg=font_color, text="Synchronisationspfad", font="Helvetia 16 bold").pack(fill=X, anchor=N, pady=5)
dir_frame = Frame(userdata_frame, bg=bg_color)
dir_entry = Entry(dir_frame, bg=bg_color, fg=font_color, font="Helvetia 16", relief=FLAT, highlightthickness=2, highlightcolor="black", highlightbackground="black")
browse_btn = Button(dir_frame, fg=rama_color, activeforeground=rama_color_active, bg=bg_color, activebackground=bg_color, text="||", font="Helvetia 16 bold", relief=FLAT, command=insert_dir)
ToolTip(browse_btn, "Ordner auswählen")
browse_btn.pack(side=RIGHT)
dir_entry.pack(fill=X, side=LEFT)
dir_frame.pack(fill=X, anchor=N, padx=8)
Button(userdata_frame, fg=font_color, activeforeground=font_color, bg=rama_color, activebackground=rama_color_active, text="Speichern", font="Helvetia 16 bold", relief=FLAT, command=submit_settings).pack(fill=X, anchor=N, padx=30, pady=10)
Button(userdata_frame, fg=font_color, activeforeground=font_color, bg=bg_color, activebackground=bg_color, text=version, font="Helvetia 10 bold", relief=FLAT, command=launch_updater).pack(side=LEFT, pady=2, padx=2)
Button(userdata_frame, fg=font_color, activeforeground=font_color, bg=bg_color, activebackground=bg_color, text="Auto Sync einrichten", font="Helvetia 10 bold", relief=FLAT, command=show_task_settings).pack(side=RIGHT, pady=2, padx=2)
username_entry.bind("<Return>", submit_settings)
password_entry.bind("<Return>", submit_settings)
dir_entry.bind("Return", submit_settings)
browse_btn.bind("<Return>", submit_settings)


# try parsing userdata from existing userdata file
try:
    # read existing userdata
    with open(f"{tmpdir}/userdata_LU.json", "r") as userdata_reader:
        userdata = json.load(userdata_reader)
    LU_dir = f"{userdata.get('dir')}/Lernumgebung OfflineSync"

    # check for wrong login data
    if not check_login():
        # incorrect userdata, fill only directory entry and show settings tab
        dir_entry.insert(0, userdata.get("dir"))
        userdata_frame.pack(expand=True, fill=BOTH)
    else:
        # correct userdata, show main tab
        main_frame.pack(expand=True, fill=BOTH)

except (FileNotFoundError, json.decoder.JSONDecodeError):
    # non existing dir or file, incorrect userdata file

    # make sure the local directory for the userdata file exists
    try:
        os.mkdir(tmpdir)
    except FileExistsError:
        pass

    # show enter userdata screen
    userdata_frame.pack(expand=True, fill=BOTH)

# check for startup arguments
if len(sys.argv) > 1 and sys.argv[1] == "-startup":
    syncLU()
    root.destroy()
    sys.exit(0)
else:
    updateLog = json.loads(v.text)
    if updateLog.get("version") != version and messagebox.askyesno("Update verfügbar", "Die Version " + updateLog.get("version") + " ist nun verfügbar. Jetzt herunterladen?"):
        launch_updater()

root.mainloop()
