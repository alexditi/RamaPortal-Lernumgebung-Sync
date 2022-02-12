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

arg_path = sys.argv[1]
arg_version = sys.argv[2]


def update():
    update_btn.config(state=DISABLED)
    info_label.config(text="Downloading new file LernumgebungSynchronisation.exe")
    root.update_idletasks()
    with open(path.get(), "wb+") as new_file:
        new_file.write(requests.get(f"https://github.com/alexditi/RamaPortalClientsided-Projects/raw/{version.get()}/Lernumgebung Sync/LernumgebungSynchronisation.exe").content)
    info_label.config(text="Installation abgeschlossen")
    root.update_idletasks()
    sleep(0.5)
    update_btn.config(text="Schließen", state=NORMAL, command=close)
    root.update_idletasks()


def close():
    subprocess.Popen([path.get()], shell=False, stdin=None, stdout=None, stderr=None, close_fds=True, creationflags=subprocess.DETACHED_PROCESS)
    sleep(1)
    root.destroy()
    sys.exit(0)


root = Tk()
root.wm_title("LU Sync Updater")
root.wm_minsize(100, 100)

# search for icon
# noinspection PyBroadException
try:
    base_path = sys._MEIPASS + "\\"
except Exception:
    base_path = ""
root.iconbitmap(os.path.join(base_path, "../logo_rama.ico"))

main_frame = Frame(root, bg=bg_color)

info_label = Label(main_frame, text="Lernumgebung Synchronisation Updater", bg=bg_color, fg=font_color, font="Helvetia 13")
info_label.pack(padx=5, pady=7)

version_frame = Frame(main_frame, bg=bg_color)
Label(version_frame, text="Update to Version: ", bg=bg_color, fg=font_color, font="Helvetia 12").pack(side=LEFT)
version = Entry(version_frame, bg=bg_color, fg=font_color, width=16, font="Helvetia 12")
version.pack(side=LEFT)
version.insert(0, arg_version)
version_frame.pack(expand=True, fill=X, padx=5, pady=7)

path_frame = Frame(main_frame, bg=bg_color)
Label(path_frame, text="Old File: ", bg=bg_color, fg=font_color, font="Helvetia 12").pack(side=LEFT)
path = Entry(path_frame, bg=bg_color, fg=font_color, font="Helvetia 12", width=24)
path.pack(side=LEFT)
path.insert(0, arg_path)
path_frame.pack(expand=True, fill=X, padx=5, pady=7)

update_btn = Button(main_frame, text="Update starten", command=update, bg=rama_color, activebackground=rama_color_active, fg=font_color, activeforeground=font_color, font="Helvetia 13 bold", relief=FLAT)
update_btn.pack(side=BOTTOM, pady=5)

main_frame.pack(expand=True, fill=BOTH)

root.mainloop()
