from tkinter import *
import requests
import subprocess
import os
from time import sleep

# color constants
bg_color = "#282828"
font_color = "light grey"
rama_color = "#A51320"
rama_color_active = "#9E1220"

installation_path = sys.argv[1]
arg_version = sys.argv[2]


def update():
    update_btn.config(state=DISABLED)
    info_label.config(text="Downloading new file LernumgebungSynchronisation " + arg_version)
    root.update_idletasks()
    with open(installation_path, "wb+") as new_file:
        new_file.write(requests.get(f"https://github.com/alexditi/RamaPortalClientsided-Projects/raw/{version.get()}/Lernumgebung Sync/LernumgebungSynchronisation.exe").content)
    info_label.config(text="Installation abgeschlossen")
    root.update_idletasks()
    sleep(0.5)
    update_btn.config(text="Schließen", state=NORMAL, command=close)
    root.update_idletasks()


def close():
    subprocess.Popen([installation_path], shell=False, stdin=None, stdout=None, stderr=None, close_fds=True, creationflags=subprocess.DETACHED_PROCESS)
    sleep(1)
    root.destroy()
    exit(0)


root = Tk()
root.wm_title("LU Sync Updater")
root.wm_minsize(100, 100)

# search for icon
# noinspection PyBroadException
try:
    base_path = sys._MEIPASS + "\\"
except Exception:
    base_path = ""
root.iconbitmap(os.path.join(base_path, "logo_rama.ico"))

main_frame = Frame(root, bg=bg_color)
info_label = Label(main_frame, text="Lernumgebung Synchronisation Updater", bg=bg_color, fg=font_color, font="Helvetia 13")
info_label.pack(padx=5, pady=7)
version_frame = Frame(main_frame, bg=bg_color)
Label(version_frame, text="Update auf Version: ", bg=bg_color, fg=font_color, font="Helvetia 12").pack(side=LEFT)
version = Entry(version_frame, bg=bg_color, fg=font_color, width=5, font="Helvetia 12")
version.pack(side=LEFT)
version.insert(0, arg_version)
version_frame.pack(expand=TRUE, fill=X, padx=5, pady=7)
update_btn = Button(main_frame, text="Update starten", command=update, bg=rama_color, activebackground=rama_color_active, fg=font_color, activeforeground=font_color, font="Helvetia 13 bold", relief=FLAT)
update_btn.pack(side=BOTTOM, pady=5)
main_frame.pack(expand=True, fill=BOTH)
root.mainloop()
