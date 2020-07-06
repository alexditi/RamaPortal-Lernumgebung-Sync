import requests
import os
import json
from bs4 import BeautifulSoup
from queue import LifoQueue
from tkinter import *
from tkinter import messagebox, filedialog


# some global variables
tmpdir = os.environ["localappdata"].replace("\\", "/") + "/RamaPortal Client"
url = "https://portal.rama-mainz.de"
s = requests.Session()
error_log = []
userdata_reader = ""
userdata = {}
LU_dir = ""

# color variables
bg_color = "#282828"
font_color = "light grey"
rama_color = "#A51320"
rama_color_active = "#9E1220"


def check_login():
    return not (BeautifulSoup(s.post(url + "/index.php", {"txtBenutzer": userdata.get("username"), "txtKennwort": userdata.get(
            "password")}).text, features="html.parser").text.find("angemeldet als") == -1)


def create_userdata_file(event=""):
    global userdata_reader, userdata, LU_dir
    userdata_creator = open(tmpdir + "/userdata_LU.json", "w+")
    json.dump({"username": username_entry.get(), "password": password_entry.get(), "dir": dir_entry.get()}, userdata_creator)
    userdata_creator.close()
    del userdata_creator
    # open reader
    userdata_reader = open(tmpdir + "/userdata_LU.json", "r")
    userdata = json.load(userdata_reader)
    userdata_reader.close()
    del userdata_reader
    LU_dir = userdata.get("dir") + "/Lernumgebung OfflineSync"
    if check_login():
        userdata_frame.pack_forget()
        main_frame.pack(expand=True, fill=BOTH)
    else:
        username_entry.delete(0, END)
        password_entry.delete(0, END)
        messagebox.showerror("Anmeldung fehlgeschlagen!", "Falscher Benutzername oder Passwort")


def insert_dir():
    dir_entry.delete(0, END)
    dir_entry.insert(0, filedialog.askdirectory())


def mk_dir(path):
    global error_log
    try:
        try:
            os.mkdir(path)
        except FileExistsError:
            pass
    except Exception as ex:
        error_log.append(("Folender Pfad konnte nicht erstellt werden: ", ex, path))


def download_file(file, dir_string):
    global error_log
    print("Downloading File", file.get("name"), "to", dir_string + "/" + file.get("name") + "." + file.get("typ"))

    # noinspection PyBroadException
    try:
        resp = s.get(url + "/edu/edufile.php?id=" + file.get("id") + "&download=1")
        ext = file.get("typ")
        # sort out non standard files
        if ext == "handschriftl Notiz":
            # not yet implemented
            pass
        elif ext == "tabellenkalkulation":
            # not yet implemented
            pass
        elif ext == "embedded link":
            # not yet implemented
            pass
        elif ext == "img":
            # image
            s_file = open(dir_string + "/" + file.get("name") + ".jpg", "wb+")
            s_file.write(resp.content)
            s_file.close()
        elif ext == "audio":
            # not yet implemented
            pass
        elif ext == "ytb":
            # youtube link
            s_file = open(dir_string + "/" + file.get("name") + ".url", "w+")
            s_file.write("[{000214A0-0000-0000-C000-000000000046}]\n")
            s_file.write("Prop3=19,11\n[InternetShortcut]\nIDList=\n")
            s_file.write("URL=https://www.youtube.com/watch?v=" + resp.text)
            s_file.close()
        elif ext == "video":
            # not yet implemented
            pass
        elif ext == "test":
            # not yet implemented
            pass
        elif ext == "PhET simulation":
            # not yet implemented
            pass
        else:
            # ext is a valid file extension
            s_file = open(dir_string + "/" + file.get("name") + "." + ext, "wb+")
            s_file.write(resp.content)
            s_file.close()
    except Exception as ex:
        error_log.append(("Beim speichern der folgenden Datei ist ein Fehler aufgetreten: ", ex, file))


def get_material_list(href):
    resp = s.get(href).text
    resp = resp[resp.find("window.materialListe = ") + 23:]
    resp = resp[:resp.find("</script>") - 1]
    return json.loads(resp)


def syncLU():
    global error_log

    # get groups
    resp = s.get(url + "/edu/edumain.php").text
    groupList = list()
    groupmanager = resp[resp.find("class='flist'"):resp.find("class='mlist'")]
    groupmanager = groupmanager.replace("class='flist' ", "")
    while groupmanager.find("gruppe") != -1:
        groupList.append(groupmanager[groupmanager.find("title='") + 7:groupmanager.find("class='felem'") - 7])
        groupmanager = groupmanager.replace("title=", "", 1).replace("class='felem'", "", 1)
        groupList.append(groupmanager[groupmanager.find("gruppe=") + 7:groupmanager.find("&section")])
        groupmanager = groupmanager.replace("gruppe=", "", 1).replace("&section", "", 1)

    # get each group's file directory
    i = 0
    dir_stack = LifoQueue()
    mk_dir(LU_dir)

    while i < len(groupList):
        for sect, dir_sa in [("publ", "Öffentlich"), ("priv", "Privat")]:
            print(groupList[i], groupList[i + 1], dir_sa)

            # access main directory, create folder
            current_material_list = get_material_list(url + "/edu/edumain.php?gruppe=" + groupList[i + 1] + "&section=" + sect)
            dir_string = LU_dir + "/" + groupList[i]
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
                        ">", "").replace("|", "")
                    while file_name[len(file_name) - 1] == " ":
                        file_name = file_name[:-1]
                    current_file.update({"name": file_name})

                    if current_file.get("typ") == "dir":
                        # directory
                        dir_string += "/" + current_file.get("name")
                        mk_dir(dir_string)
                        current_material_list = get_material_list(url + "/edu/edumain.php?gruppe=" + groupList[i + 1] + "&section=publ&dir=" + current_file.get("id"))
                        n = 0
                        print("changed dir to", current_file.get("name"))
                    else:
                        # file
                        dir_stack.get()
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

        i += 2


# quick login
# if BeautifulSoup(s.post(url + "/index.php", {"txtBenutzer": userdata.get("username"), "txtKennwort": userdata.get(
#         "password")}).text, features="html.parser").text.find("angemeldet als") == -1:
#     print("Anmeldung fehlgeschlagen")
# else:
#     print("Anmeldung erfolgreich!")
#
#     syncLU()
#     for error in error_log:
#        print(error)


root = Tk()
root.wm_title("Lernumgebung Synchronisation")
root.wm_minsize(300, 300)
root.wm_maxsize(300, 300)

# main Frame
main_frame = Frame(root, bg=bg_color)

# userdata Frame
userdata_frame = Frame(root, bg=bg_color)
Label(userdata_frame, bg=bg_color, fg=font_color, text="Benutzername", font="Helvetia 16 bold").pack(fill=X, anchor=N, pady=5)
username_entry = Entry(userdata_frame, bg=bg_color, fg=font_color, font="Helvetia 16", relief=FLAT, highlightthickness=2, highlightcolor="black", highlightbackground="black")
username_entry.pack(fill=X, anchor=N, padx=8)
Label(userdata_frame, bg=bg_color, fg=font_color, text="Passwort", font="Helvetia 16 bold").pack(fill=X, anchor=N, pady=5)
password_entry = Entry(userdata_frame, bg=bg_color, fg=font_color, font="Helvetia 16", show="*", relief=FLAT, highlightthickness=2, highlightcolor="black", highlightbackground="black")
password_entry.pack(fill=X, anchor=N, padx=8)
Label(userdata_frame, bg=bg_color, fg=font_color, text="Synchronisationspfad", font="Helvetia 16 bold").pack(fill=X, anchor=N, pady=5)
dir_frame = Frame(userdata_frame, bg=bg_color)
dir_entry = Entry(dir_frame, bg=bg_color, fg=font_color, font="Helvetia 16", relief=FLAT, highlightthickness=2, highlightcolor="black", highlightbackground="black")
Button(dir_frame, fg=rama_color, activeforeground=rama_color_active, bg=bg_color, activebackground=bg_color, text="||", font="Helvetia 16 bold", relief=FLAT, command=insert_dir).pack(side=RIGHT)
dir_entry.pack(fill=X, side=LEFT)
dir_frame.pack(fill=X, anchor=N, padx=8)
Button(userdata_frame, fg="black", bg=rama_color, activebackground=rama_color_active, text="Speichern", font="Helvetia 16 bold", relief=FLAT, command=create_userdata_file).pack(fill=X, anchor=N, padx=30, pady=10)


# try parsing userdata from existing userdata file
# existing userdata file
try:
    userdata_reader = open(tmpdir + "/userdata_LU.json", "r")
    userdata = json.load(userdata_reader)
    userdata_reader.close()
    del userdata_reader
    LU_dir = userdata.get("dir") + "/Lernumgebung OfflineSync"

    # check for wrong login data
    if not check_login():
        dir_entry.insert(0, userdata.get("dir"))
        userdata_frame.pack(expand=True, fill=BOTH)
    else:
        main_frame.pack(expand=True, fill=BOTH)

# non existing dir or file, incorrect userdata file
except (FileNotFoundError, json.decoder.JSONDecodeError):
    try:
        # create dir
        os.mkdir(tmpdir)
    except FileExistsError:
        pass
    # show enter userdata screen
    userdata_frame.pack(expand=True, fill=BOTH)

root.mainloop()
