from tkinter import *
from tkinter import messagebox
import requests
import json
from bs4 import BeautifulSoup
from threading import Thread
import copy as cpy
from time import sleep
import webbrowser
import os


class ChatBtn(object):
    btn = Button
    chat_id = 0

    def __init__(self, btn, chat_id):
        self.btn = btn
        self.chat_id = chat_id
        self.btn.config(command=lambda: display_chat(self.chat_id))

    def get_btn(self):
        return self.btn


class DwnlBtn(object):
    btn = Button
    href = ""

    def __init__(self, btn, href):
        self.btn = btn
        self.href = href
        self.btn.config(command=lambda: open_from_URL(self.href))

    def get_btn(self):
        return self.btn


class ScrollableFrame(Frame):

    canvas = Canvas

    def on_scroll(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta / 80)), "units")

    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.canvas = Canvas(self)
        scrollbar = Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.bind_all("<MouseWheel>", self.on_scroll)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")


# webbrowser.register("windows-default", None)

# setting up root widget
root = Tk()
root.title("Rama Portal")
root.geometry("1000x800")

# decoration constants
bg_color = "#282828"
font_color = "light grey"
rama_color = "#A51320"
rama_color_active = "#9E1220"

# some variables
default_entry = ["Benutzername", "Passwort"]
last_focus = ""
url = "https://portal.rama-mainz.de/"
s = requests.Session()
icon = PhotoImage(file="icon.png")
pdfIcon = PhotoImage(file="pdfIcon.png")
logo = PhotoImage(file="logo_rama.png")
chatBtns = [ChatBtn(Button(), 0) for _ in range(15)]
chats = [{"id": "", "name": ""} for _ in range(15)]
msgArea = [Frame()]
msgMField = [Message()]
crChat = -1
chatUpdater = Thread
stopUpdate = False
prev_msg = []
sessid = dict()
cTemp = 0
loginName = ""
tmpdir = os.environ["localappdata"].replace("\\", "/") + "/RamaPortal Client"

# copy userdata to dictionary
try:
    userdata_reader = open(tmpdir + "/userdata_LU.json", "r")
except FileNotFoundError:
    # non existing dir or file
    try:
        # create dir
        os.mkdir(tmpdir)
    except FileExistsError:
        pass
    # create file
    userdata_creator = open(tmpdir + "/userdata_LU.json", "w+")
    json.dump({"username": "", "password": "", "dir": ""}, userdata_creator)
    userdata_creator.close()
    del userdata_creator
    # open reader
    userdata_reader = open(tmpdir + "/userdata_LU.json", "r")

userdata = json.load(userdata_reader)
userdata_reader.close()
del userdata_reader
username = ""
password = ""


# Login Entry management
def on_entry_focus(event):
    global last_focus
    if event.widget.get() in default_entry:
        last_focus = event.widget.get()
        event.widget.delete(0, END)


def on_entry_left(event):
    if event.widget.get() == "":
        event.widget.insert(0, last_focus)


# window closing manager
def on_closing(event=""):
    global stopUpdate
    if messagebox.askokcancel("Verlassen", "RAMA Portal verlassen?"):
        userdata_writer = open(tmpdir + "/userdata.json", 'w')
        json.dump(userdata, userdata_writer)
        userdata_writer.close()
        stopUpdate = True
        for i in range(cTemp):
            os.remove("temp/temp" + str(i) + ".pdf")
        root.destroy()


# login verification
def login(event=""):
    global username, password, userdata, sessid, loginName
    resp = s.post(url + "main.php", {"txtBenutzer": usernameEntry.get(), "txtKennwort": passwordEntry.get()})
    if resp.text.find("Falscher Anmeldename") != -1:
        label_wrongPassword.pack_forget()
        label_wrongUsername.pack(pady=30)
        return False
    elif resp.text.find("Login fehlgeschlagen") != -1:
        label_wrongUsername.pack_forget()
        label_wrongPassword.pack(pady=30)
        return False
    else:
        # save login data
        userdata.update({"username": usernameEntry.get(), "password": passwordEntry.get()})
        username = userdata.get("username")
        password = userdata.get("password")

        # get client name
        resp = s.get(url + "/index.php?redir=no")
        loginName = BeautifulSoup(resp.text, features="html.parser").text
        loginName = loginName[loginName.find("angemeldet als") + 15:loginName.find(".Zur Startseite")]

        # set client infos
        accoutLabel.config(text="Angemeldet als\n" + loginName + "\n(" + username + ")")
        s.get(url + "/main.php?extLogin=ja")
        usernameEntry.delete(0, END)
        usernameEntry.insert(0, "Benutzername")
        passwordEntry.delete(0, END)
        passwordEntry.insert(0, "Passwort")
        label_wrongUsername.pack_forget()
        label_wrongPassword.pack_forget()

        # load data
        # 1. chat info
        r = s.get(url + "chat.php")
        chatinfo = r.text
        for i1 in range(1, 15):
            idfinder = ""
            namefinder = ""
            ind = chatinfo.find("sidebar_btn_" + str(i1))
            if ind == -1:
                break
            while chatinfo[ind] != '>':
                idfinder += chatinfo[ind]
                ind += 1
            ind += 1
            while chatinfo[ind] != '<':
                namefinder += chatinfo[ind]
                ind += 1
            chats[i1].update({"id": idfinder[(idfinder.find("id=") + 3):-1], "name": namefinder})

        # 2. chatBtn init
        for i2 in range(1, 15):
            if chats[i2].get("name") == "":
                chatBtns[i2].get_btn().config(bg=bg_color, state=DISABLED)
            else:
                chatBtns[i2].get_btn().config(text=chats[i2].get("name"))
                chatBtns[i2].chat_id = chats[i2].get("id")

        sessid = {"name": "PHPSESSID", "value": s.cookies.get("PHPSESSID")}

        hide_login()
        show_main()
        return True


def logout():
    global userdata, username, password
    userdata.update({"username": "", "password": ""})
    username = ""
    password = ""
    accoutLabel.config(text="Angemeldet als\n")
    s.get(url + "index.php?abmelden=1")
    hide_options()
    hide_main()
    show_login()


def change_password():
    # s.get(url + "index.php?passwd=1")
    # r1 = s.post(url + "index.php?passwd=1", {"altKennwort": "sander", "neuKennwort": "sander2003", "neu2Kennwort": "sander2003"})
    messagebox.showinfo("Noch nicht verfügbar", "Dieses Feature ist aktuell noch nicht verfügbar.")


def display_chat(chat_id):
    global msgFrame, msgArea, msgMField, crChat, prev_msg
    crChat = chat_id
    messages = []

    if chat_id != -1:
        r1 = s.get(url + "/chat.php?id=" + str(chat_id))
        c = r1.text

        # set up c
        msgFinder = ""
        start = c.find("<td class='message-new'>")
        while msgFinder.find("<tr class='placeholder'></tr>") == -1:
            msgFinder += c[start]
            start += 1
        c = c[start:]

        # eval c
        while True:
            msgProvider = ""
            msgFinder = ""
            speakerFinder = ""
            docFinder = ""
            tag = ""

            start = c.find("<tr>")
            if start == -1:
                break
            while msgProvider.find("</tr>") == -1:
                msgProvider += c[start]
                start += 1
            if msgProvider.find(
                    "<input type='text' id='filenam' name='filenam' size='50' style='background:#eee;' placeholder='jpg,jpeg,gif,png,tif,tiff,bmp oder pdf' readonly='readonly' value=''>") != -1:
                break

            # in this if clause, the message part will be decoded
            if msgProvider.find("<tr><td class='separator'></td></tr>") == -1:

                # search for speaker
                got = 0
                if msgProvider.find("speaker-right lehrer") != -1:
                    got = msgProvider.find("speaker-right lehrer")
                    tag = "t"
                elif msgProvider.find("speaker-right ") != -1:
                    got = msgProvider.find("speaker-right")
                    tag = "o"
                if msgProvider.find("speaker-left") != -1:
                    got = msgProvider.find("speaker-left")
                    tag = "m"
                while speakerFinder.find("</td>") == -1:
                    speakerFinder += msgProvider[got]
                    got += 1
                speakerFinder = speakerFinder.replace("<br />", "\n")
                speakerFinder = speakerFinder.replace("</td>", "")
                speakerFinder = BeautifulSoup(speakerFinder, features="html.parser").text
                speakerFinder = speakerFinder.replace("speaker-right lehrer'>", "")
                speakerFinder = speakerFinder.replace("speaker-right '>", "")
                speakerFinder = speakerFinder.replace("speaker-left'>", "")

                # search for message
                got = 0
                if msgProvider.find("message-right lehrer") != -1:
                    got = msgProvider.find("message-right lehrer")
                    tag = "t"
                elif msgProvider.find("message-right ") != -1:
                    got = msgProvider.find("message-right ")
                    tag = "o"
                if msgProvider.find("message-left") != -1:
                    got = msgProvider.find("message-left")
                    tag = "m"
                while msgFinder.find("</td>") == -1:
                    msgFinder += msgProvider[got]
                    got += 1
                msgFinder = msgFinder.replace("</td>0", "")

                # search for doc in message
                if msgFinder.find("<a href='") != -1:
                    dot = msgFinder.find("<a href='")
                    dot += 9
                    while docFinder.find("'>") == -1:
                        docFinder += msgFinder[dot]
                        dot += 1
                    docFinder = docFinder.replace("'>", "")

                msgFinder = BeautifulSoup(msgFinder, features="html.parser").text
                msgFinder = msgFinder.replace("message-right lehrer'>", "")
                msgFinder = msgFinder.replace("message-right '>", "")
                msgFinder = msgFinder.replace("message-left'>", "")

                messages.append((speakerFinder, msgFinder, tag, docFinder))

            c = c.replace("<tr>", "<do>", 1)

    # check for new messages/other chat selection
    if messages != prev_msg:
        # set up scrollable Chat Frame
        msgFrame.pack_forget()
        del msgFrame.scrollable_frame
        del msgFrame
        msgFrame = ScrollableFrame(chatsFrame, bg=bg_color)
        msgFrame.scrollable_frame.option_add("*background", bg_color)

        # set up single message frames
        for msgField in msgArea:
            msgField.pack_forget()
            del msgField
        del msgArea
        msgArea = [Frame() for _ in range(len(messages))]

        # set up message widget
        for msgField in msgMField:
            msgField.pack_forget()
            del msgField
        del msgMField
        msgMField = [Message() for _ in range(len(messages))]

        for i, msgi in enumerate(messages):
            speaker, msg, tag, docUrl = msgi

            nclr = ""
            nclrF = ""
            if tag == "o":
                nclr = bg_color
                nclrF = font_color
            if tag == "t":
                nclr = "orange"
                nclrF = "black"
            if tag == "m":
                nclr = "#00B700"
                nclrF = "black"

            # disp single message Frames
            msgArea[i] = Frame(msgFrame.scrollable_frame, bg=nclr)
            msgArea[i].pack(side="top", expand=True, fill=X)
            Label(msgArea[i], text=speaker, font="Arial 12", bg=nclr, fg=nclrF, width=15).pack(fill=X, side="left", anchor=N)
            if docUrl != "":
                DwnlBtn(Button(msgArea[i], image=pdfIcon, bg=nclr, activebackground=nclr, relief=FLAT, borderwidth=0, anchor=NW), docUrl).get_btn().pack(side="top", expand=True, fill=X, pady=5)
            msgMField[i] = Message(msgArea[i], text=msg, bg=nclr, fg=nclrF, font="Arial 12", anchor=NW, width=700)
            msgMField[i].pack(expand=True, fill=X, side="left", anchor=N)
            Frame(msgFrame.scrollable_frame, bg=bg_color, height=15).pack(side="top", expand=True, fill=X)
            Frame(msgFrame.scrollable_frame, bg=rama_color, height=5).pack(side="top", expand=True, fill=X)
            Frame(msgFrame.scrollable_frame, bg=bg_color, height=15).pack(side="top", expand=True, fill=X)

        msgFrame.pack(side="top", expand=True, fill=BOTH)

    prev_msg = cpy.deepcopy(messages)


def display_direct():
    pass


def update_chats():
    while not stopUpdate:
        if crChat != -1:
            display_chat(crChat)
        sleep(3)


def send_new_msg():
    msg = message.get("1.0", END)
    if len(msg) > 1000:
        messagebox.showwarning("Zeichenlimit erreicht", "Die Nachricht darf nicht länger als 1000 Zeichen sein!")
    elif msg != '' and crChat != -1:
        s.post("https://portal.rama-mainz.de/chat.php?id=" + str(crChat) + "&action=addmsg", {"msgtext": msg})
        sleep(0.1)
        message.delete("1.0", END)
        display_chat(crChat)


def attachFile():
    pass


def open_from_URL(href):
    global cTemp, browser
    r = s.get(url + href, allow_redirects=TRUE)
    open("temp/temp" + str(cTemp) + ".pdf", "wb+").write(r.content)
    sleep(0.05)
    try:
        webbrowser.get('windows-default').open(os.path.realpath("temp\\temp" + str(cTemp) + ".pdf"))
    except Exception as e:
        print(e)
    cTemp += 1


# Building Login Framework
loginFrame = Frame(root, bg=bg_color)
Label(loginFrame, text="RAMA Portal", fg=rama_color, bg=bg_color, font="Arial 48").pack(pady=80)
label_wrongUsername = Label(loginFrame, text="Login fehlgeschlagen.\nBenutzername nicht gefunden", font="Arial 18", bg=bg_color, fg=rama_color)
label_wrongPassword = Label(loginFrame, text="Login fehlgeschlagen.\nFalsches Passwort", font="Arial 18", bg=bg_color, fg=rama_color)
usernameEntry = Entry(loginFrame, highlightcolor="black", highlightbackground="black", highlightthickness=2, relief=FLAT, fg=font_color, bg=bg_color, font="Arial 18")
usernameEntry.pack(pady=5)
usernameEntry.insert(0, "Benutzername")
usernameEntry.bind("<FocusIn>", on_entry_focus)
usernameEntry.bind("<FocusOut>", on_entry_left)
usernameEntry.bind("<Return>", login)
passwordEntry = Entry(loginFrame, highlightcolor="black", highlightbackground="black", highlightthickness=2, relief=FLAT, fg=font_color, bg=bg_color, font="Arial 18")
passwordEntry.pack(pady=5)
passwordEntry.insert(0, "Passwort")
passwordEntry.bind("<FocusIn>", on_entry_focus)
passwordEntry.bind("<FocusOut>", on_entry_left)
passwordEntry.bind("<Return>", login)
loginBtn = Button(loginFrame, text="Login", fg=font_color, bg="blue", relief=FLAT, command=login, font="Arial 18", width=19, height=1, borderwidth=0, activebackground="blue", activeforeground=font_color).pack(pady=5)

# Setting up Frames
mainFrame = Frame(root, bg=bg_color)
stundenplanFrame = Frame(root, bg=bg_color)
vertretungsplanFrame = Frame(root, bg=bg_color)
terminkalenderFrame = Frame(root, bg=bg_color)
fehlzeitenFrame = Frame(root, bg=bg_color)
agFrame = Frame(root, bg=bg_color)
klausurenFrame = Frame(root, bg=bg_color)
chatsFrame = Frame(root, bg=bg_color)
luFrame = Frame(root, bg=bg_color)
instructionLuFrame = Frame(root, bg=bg_color)
forStudentsFrame = Frame(root, bg=bg_color)
surveysFrame = Frame(root, bg=bg_color)
optionsFrame = Frame(root, bg=bg_color)


# Window Frame Manager
# Login Frame Manager
def show_login():
    loginFrame.pack(expand=True, fill=BOTH)
    root.update_idletasks()


def hide_login():
    loginFrame.pack_forget()
    root.update_idletasks()


# Main Frame Manager
def show_main():
    mainFrame.pack(expand=True, fill=BOTH)
    root.update_idletasks()


def hide_main():
    mainFrame.pack_forget()
    root.update_idletasks()


# Stundeplan Frame Manager
def show_stundenplan():
    hide_main()
    stundenplanFrame.pack(expand=True, fill=BOTH)
    root.update_idletasks()


def hide_stundenplan():
    stundenplanFrame.pack_forget()
    show_main()
    root.update_idletasks()


# Vertretungsplan Frame Manager
def show_vertretungsplan():
    hide_main()
    vertretungsplanFrame.pack(expand=True, fill=BOTH)
    root.update_idletasks()


def hide_vertretungsplan():
    vertretungsplanFrame.pack_forget()
    show_main()
    root.update_idletasks()


# Terminkalender Frame Manager
def show_terminkalender():
    hide_main()
    terminkalenderFrame.pack(expand=True, fill=BOTH)
    root.update_idletasks()


def hide_terminkalender():
    terminkalenderFrame.pack_forget()
    show_main()
    root.update_idletasks()


# Fehleiten
def show_fehlzeiten():
    hide_main()
    fehlzeitenFrame.pack(expand=True, fill=BOTH)
    root.update_idletasks()


def hide_fehlzeiten():
    fehlzeitenFrame.pack_forget()
    show_main()
    root.update_idletasks()


# AG Frame Manager
def show_ag():
    hide_main()
    agFrame.pack(expand=True, fill=BOTH)
    root.update_idletasks()


def hide_ag():
    agFrame.pack_forget()
    show_main()
    root.update_idletasks()


# Klausurenplan Frame Manager
def show_klausurenplan():
    hide_main()
    klausurenFrame.pack(expand=True, fill=BOTH)
    root.update_idletasks()


def hide_Klausurenplan():
    klausurenFrame.pack_forget()
    show_main()
    root.update_idletasks()


# Chats Frame Manager
def show_chats():
    global chatUpdater, stopUpdate
    hide_main()
    chatsFrame.pack(expand=True, fill=BOTH)
    display_chat(-1)
    display_chat(-1)

    stopUpdate = False
    chatUpdater = Thread(target=update_chats)
    chatUpdater.start()

    root.update_idletasks()


def hide_chats():
    global crChat, stopUpdate
    crChat = -1
    stopUpdate = True
    chatsFrame.pack_forget()
    show_main()
    root.update_idletasks()


# Lernumgebung Manager
def show_lernumgebung():
    hide_main()
    luFrame.pack(expand=True, fill=BOTH)
    root.update_idletasks()


def hide_lernumgebung():
    luFrame.pack_forget()
    show_main()
    root.update_idletasks()


# anleitung Lu Frame Manager
def show_instructionLU():
    hide_main()
    instructionLuFrame.pack(expand=True, fill=BOTH)
    root.update_idletasks()


def hide_instructionLU():
    instructionLuFrame.pack_forget()
    show_main()
    root.update_idletasks()


# für Schüler Frame Manager
def show_forStudents():
    hide_main()
    forStudentsFrame.pack(expand=True, fill=BOTH)
    root.update_idletasks()


def hide_forStudents():
    forStudentsFrame.pack_forget()
    show_main()
    root.update_idletasks()


# Umfragen Frame Manager
def show_surveys():
    hide_main()
    surveysFrame.pack(expand=True, fill=BOTH)
    root.update_idletasks()


def hide_surveys():
    surveysFrame.pack_forget()
    show_main()
    root.update_idletasks()


# Options Frame Manager
def show_options():
    hide_main()
    optionsFrame.pack(expand=True, fill=BOTH)
    root.update_idletasks()


def hide_options():
    optionsFrame.pack_forget()
    show_main()
    root.update_idletasks()


# Building Main Framework
Label(mainFrame, image=logo, bg=bg_color).place(x=280, y=50)
Button(mainFrame, text="Mein\nStunden-\nplan",  bg=rama_color, fg=font_color, relief=FLAT, activebackground=rama_color_active, activeforeground=font_color, borderwidth=0, font="Arial 14", command=show_stundenplan).place(width=120, height=120, x=125, y=250)
Button(mainFrame, text="Vertretungs-\nplan", bg=rama_color, fg=font_color, relief=FLAT, activebackground=rama_color_active, activeforeground=font_color, borderwidth=0, font="Arial 14", command=show_vertretungsplan).place(width=120, height=120, x=250, y=250)
Button(mainFrame, text="Termin-\nkalender", bg=rama_color, fg=font_color, relief=FLAT, activebackground=rama_color_active, activeforeground=font_color, borderwidth=0, font="Arial 14", command=show_terminkalender).place(width=120, height=120, x=375, y=250)
Button(mainFrame, text="Fehlzeiten", bg=rama_color, fg=font_color, relief=FLAT, activebackground=rama_color_active, activeforeground=font_color, borderwidth=0, font="Arial 14", command=show_fehlzeiten).place(width=120, height=120, x=500, y=250)
Button(mainFrame, text="Arbeits-\ngemein-\nschaften", bg=rama_color, fg=font_color, relief=FLAT, activebackground=rama_color_active, activeforeground=font_color, borderwidth=0, font="Arial 14", command=show_ag).place(width=120, height=120, x=625, y=250)
Button(mainFrame, text="Klausuren-\nplan MSS", bg=rama_color, fg=font_color, relief=FLAT, activebackground=rama_color_active, activeforeground=font_color, borderwidth=0, font="Arial 14", command=show_klausurenplan).place(width=120, height=120, x=750, y=250)
Button(mainFrame, text="Chat-\ngruppen", bg=rama_color, fg=font_color, relief=FLAT, activebackground=rama_color_active, activeforeground=font_color, borderwidth=0, font="Arial 14", command=show_chats).place(width=120, height=120, x=125, y=375)
Button(mainFrame, text="Lern-\numgebung", bg=rama_color, fg=font_color, relief=FLAT, activebackground=rama_color_active, activeforeground=font_color, borderwidth=0, font="Arial 14", command=show_lernumgebung).place(width=120, height=120, x=250, y=375)
Button(mainFrame, text="Anleitung\nzur Lern-\numgebung", bg=rama_color, fg=font_color, relief=FLAT, activebackground=rama_color_active, activeforeground=font_color, borderwidth=0, font="Arial 14", command=show_instructionLU).place(width=120, height=120, x=375, y=375)
Button(mainFrame, text="Materialien\nfür Schüler", bg=rama_color, fg=font_color, relief=FLAT, activebackground=rama_color_active, activeforeground=font_color, borderwidth=0, font="Arial 14", command=show_forStudents).place(width=120, height=120, x=500, y=375)
Button(mainFrame, text="Umfragen", bg=rama_color, fg=font_color, relief=FLAT, activebackground=rama_color_active, activeforeground=font_color, borderwidth=0, font="Arial 14", command=show_surveys).place(width=120, height=120, x=625, y=375)
Button(mainFrame, text="Einstellungen", bg=rama_color, fg=font_color, relief=FLAT, activebackground=rama_color_active, activeforeground=font_color, borderwidth=0, font="Arial 14", command=show_options).place(width=120, height=120, x=750, y=375)

# Building Stundenplan Framework
Button(stundenplanFrame, command=hide_stundenplan, bg=bg_color, activebackground=bg_color, font="Arial 14", relief=FLAT, highlightcolor="black", highlightthickness=2, borderwidth=0, image=icon).pack(anchor=N+W, padx=8, pady=8)

# Building Vertretungsplan Framework
Button(vertretungsplanFrame, command=hide_vertretungsplan, bg=bg_color, activebackground=bg_color, font="Arial 14", relief=FLAT, highlightcolor="black", highlightthickness=2, borderwidth=0, image=icon).pack(anchor=N+W, padx=8, pady=8)

# Building Kalender Framework
Button(terminkalenderFrame, command=hide_terminkalender, bg=bg_color, activebackground=bg_color, font="Arial 14", relief=FLAT, highlightcolor="black", highlightthickness=2, borderwidth=0, image=icon).pack(anchor=N+W, padx=8, pady=8)

# Building Fehlzeiten Framework
Button(fehlzeitenFrame, command=hide_fehlzeiten, bg=bg_color, activebackground=bg_color, font="Arial 14", relief=FLAT, highlightcolor="black", highlightthickness=2, borderwidth=0, image=icon).pack(anchor=N+W, padx=8, pady=8)

# Building Ags Framework
Button(agFrame, command=hide_ag, bg=bg_color, activebackground=bg_color, font="Arial 14", relief=FLAT, highlightcolor="black", highlightthickness=2, borderwidth=0, image=icon).pack(anchor=N+W, padx=8, pady=8)

# Building Klausurenplan Framework
Button(klausurenFrame, command=hide_Klausurenplan, bg=bg_color, activebackground=bg_color, font="Arial 14", relief=FLAT, highlightcolor="black", highlightthickness=2, borderwidth=0, image=icon).pack(anchor=N+W, padx=8, pady=8)

# Building Chats Framework
Button(chatsFrame, command=hide_chats, bg=bg_color, activebackground=bg_color, font="Arial 14", relief=FLAT, highlightcolor="black", highlightthickness=2, borderwidth=0, image=icon).pack(side="left", anchor=N, padx=8, pady=8)
chatBtns[0] = Button(chatsFrame, text="Direkt", bg=rama_color, activebackground=rama_color, fg=font_color, activeforeground=font_color, relief=FLAT, borderwidth=0, font="Arial 16", width=10, height=1)
chatBtns[0].place(x=0, y=100)
for b in range(1, 15):
    chatBtns[b] = ChatBtn(Button(chatsFrame, bg=rama_color, activebackground=rama_color_active, fg=font_color, activeforeground=font_color, relief=FLAT, borderwidth=0, height=1, font="Arial 16", width=10), 0)
    chatBtns[b].get_btn().place(x=0, y=100 + b*42)
Frame(chatsFrame, bg=bg_color, height=100).pack(anchor=NE, fill=X)
newmsgFrame = Frame(chatsFrame, bg="white", height=122)
newmsgFrame.pack(side="top", fill=X)
msgFrame = ScrollableFrame(chatsFrame, bg=bg_color)
msgFrame.pack(expand=True, fill=BOTH, side="top")
msgManageFrame = Frame(newmsgFrame, bg=bg_color)
msgManageFrame.grid(row=1, column=1, rowspan=2, columnspan=1, sticky=NSEW)
Button(msgManageFrame, text="Senden", width=14, bg=bg_color, fg=rama_color, activebackground=bg_color, activeforeground=rama_color_active, font="Arial 12 bold", relief=FLAT, command=send_new_msg).grid(row=1, column=1, pady=10)
Button(msgManageFrame, text="Datei anhängen", width=14, bg=bg_color, fg=rama_color, activeforeground=rama_color_active, activebackground=bg_color, font="Arial 12 bold", relief=FLAT, command=attachFile).grid(row=2, column=1, pady=10)
message = Text(newmsgFrame, bg=bg_color, fg=font_color, font="Arial 12", height=6)
message.grid(row=1, column=2, rowspan=2)

Frame(newmsgFrame, bg=rama_color, height=5).grid(row=3, column=1, columnspan=2, sticky=NSEW)
Frame(newmsgFrame, bg=bg_color, height=15).grid(row=4, column=1,  columnspan=2, sticky=NSEW)

# Building Lernumgebung Framework
Button(luFrame, command=hide_lernumgebung, bg=bg_color, activebackground=bg_color, font="Arial 14", relief=FLAT, highlightcolor="black", highlightthickness=2, borderwidth=0, image=icon).pack(anchor=N+W, padx=8, pady=8)

# Building Anleitung LU Framework
Button(instructionLuFrame, command=hide_instructionLU, bg=bg_color, activebackground=bg_color, font="Arial 14", relief=FLAT, highlightcolor="black", highlightthickness=2, borderwidth=0, image=icon).pack(anchor=N+W, padx=8, pady=8)

# Building für Schüler Framework
Button(forStudentsFrame, command=hide_forStudents, bg=bg_color, activebackground=bg_color, font="Arial 14", relief=FLAT, highlightcolor="black", highlightthickness=2, borderwidth=0, image=icon).pack(anchor=N+W, padx=8, pady=8)

# Building Umfragen Framework
Button(surveysFrame, command=hide_surveys, bg=bg_color, activebackground=bg_color, font="Arial 14", relief=FLAT, highlightcolor="black", highlightthickness=2, borderwidth=0, image=icon).pack(anchor=N+W, padx=8, pady=8)

# Building Options Framework
Button(optionsFrame, command=hide_options, bg=bg_color, activebackground=bg_color, font="Arial 14", relief=FLAT, highlightcolor="black", highlightthickness=2, borderwidth=0, image=icon).pack(anchor=N+W, padx=8, pady=8)
accoutLabel = Label(optionsFrame, bg=bg_color, fg=font_color, text="Angemeldet als\n" + username, font="Arial 24")
accoutLabel.pack(pady=50)
Button(optionsFrame, text="Abmelden", width=16, command=logout, bg=rama_color, activebackground=rama_color_active, fg=font_color, activeforeground=font_color, relief=FLAT, borderwidth=0, font="Arial 18").pack(pady=10)
Button(optionsFrame, text="Passwort ändern", width=16, command=change_password, bg=rama_color, activebackground=rama_color_active, fg=font_color, activeforeground=font_color, relief=FLAT, borderwidth=0, font="Arial 18").pack(pady=5)

# root closing action
root.protocol("WM_DELETE_WINDOW", on_closing)
root.bind("<Alt-F4>", on_closing)

# check for deposited userdata
if userdata.get("password") == "" and userdata.get("username") == "":
    show_login()
else:
    usernameEntry.delete(0, END)
    passwordEntry.delete(0, END)
    usernameEntry.insert(0, userdata.get("username"))
    passwordEntry.insert(0, userdata.get("password"))
    if login():
        show_main()
    else:
        show_login()

root.mainloop()
