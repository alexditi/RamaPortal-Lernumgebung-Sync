# RamaPortal Lernumgebung Synchronisation

## Überblick

Die Lernumgebung Synchronisation ist ein Tool, mit dem man seine persönliche Lernumgebung aus dem
[RamaPortal](https://portal.rama-mainz.de "Zum RamaPortal") herunterladen kann, um die Dateien offline auf dem PC zur
Verfügung zu haben.  
Zum Benutzen des Tools wird nur die Datei [LernumgebungSynchronisation.exe](https://github.com/alexditi/RamaPortal-Lernumgebung-Sync/raw/master/LernumgebungSynchronisation.exe "Zum Download")
benötigt. Der Downloadlink ist auch unter dem neuesten Release zu finden.

## Benutzung

Die .exe Datei wurde unter Windows 10 kompiliert, d.h. sie ist ausgelegt für Windows 10, sollte aber auch auf Windows 11
laufen, was jedoch noch nicht getestet wurde.  

### Erster Start

Beim ersten Starten der LernumgebungSynchronisation.exe Datei kann es sein, dass der Windows Defender wahrscheinlich das
Ausführen blockiert. Um es zuzulassen, „weitere Informationen“ anklicken und dann „Trotzdem ausführen“ auswählen.  
Jetzt wird ein Anmeldefeld angezeigt, in das die eigenen Anmeldedaten zum RamaPortal eingegeben werden müssen. Diese
werden gespeichert, sodass man sie nicht mehr eingeben muss. Über den Button neben dem Passwort Eingabefeld kann dessen
Sichtbarkeit umgeschaltet werden. Außerdem muss ein Synchronisationspfad angegeben werden, in dem der Ordner erstellt
wird, in den die Lernumgebung heruntergeladen wird. Über den Button daneben kann ein Dialog geöffnet werden, in dem der
Dateipfad im Explorer ausgewählt werden kann.

### Hauptmenü

Im Hauptmenü wird über den Button "Starte Synchronisation" das Herunterladen gestartet. Die Checkbox nur neue
Synchronisieren sorgt dafür, dass nicht jede Datei heruntergeladen wird, sondern nur die, die noch nicht offline
verfügbar sind. Dabei werden jedoch Änderungen an einer Datei in der Lernumgebung nicht synchronisiert, da nur auf das
Vorhandensein einer Datei überprüft wird. Will man also alle Dateien auch aktualisieren, kann diese Checkbox abgewählt
werden. Die zweite Checkbox "Ordner vor Update löschen" löscht den gesamten LU Sync Ordner vor dem Herunterladen, sodass
überschüssige Dateien, die in der Lernumgebung schon gelöscht wurden, auch offline gelöscht werden. Dabei werden aber
**alle** Dateien in dem Ordner gelöscht. Diese beiden etwas umständlichen Optionen zum Aufräumen der Dateien sind aber
notwendig, da die Lernumgebung nicht als Cloud System ausgelegt ist zu Offline Synchronisation und daher kein Version
Log besitzt, in dem Änderungen von Dateien gespeichert werden.

### Einstellungsmenü

Im Einstellungsmenü können Anmeldedaten sowie Synchronisationspfad geändert werden. Wenn der Synchronisationspfad
geändert wird, hat man die Möglichkeit auszuwählen, ob die Dateien aus dem alten Ordner in den neuen verschoben oder
kopiert werden sollen, oder nichts von beiden gemacht werden soll.

## Andere Dateien im Repo

Im Repository finden sich neben der LernumgebungSynchronisation.exe Datei noch andere Dateien:
* LU_updater.exe: Ein Updater, der automatisch heruntergeladen wird, wenn eine neue Version verfügbar ist und diese dann 
installiert
* LernumgebungSynchronisation.pyw: Der Python Sourcecode für das Tool
* LU_updater.py: Der Python Sourcecode für den Updater
* README.md: Diese Datei mit den Informationen
* logo_rama.ico: Das App Logo
* updateLog.json: Versionsnummer der neuesten Version für den Updater.

## Sourcecode

Der Sourcecode ist in der .pyw bzw. in der .py Datei zu finden. Der Code wird in Python 3.8 entwickelt, sollte aber auch
in neueren Pythonversionen funktionieren. Es werden die beiden zusätzlichen Libraries `requests` und `beautifulsoup4`
benötigt (Installation über pip mit `pip install beatifulsoup4` und `pip install requests`). Auch der Sourcecode ist nur
auf Windows funktionell, denn es wird auf die Windows Umgebungsvariablen zugegriffen.

## Option -startup

Wird die Lernumgebung Synchronisation mit dem Argument `-startup` gestartet (zum Beispiel über CMD), so startet direkt
ein Synchronisationsvorgang. Sobald dieser beendet ist, schließt das Programm wieder. Das kann verwendet werden, um
beispielsweise einen automatischen Synchronisationsvorgang beim PC-Start einzurichten. Das geht beispielsweise über die
Windows Aufgabenplanung.

## TODO v7.0 mit Repo Restructure, sodass updateLog aus der neuen Datei ausgelesen wird
!!! auf alle Links in beiden Dateien überprüfen, ob sie aktualisiert werden müssen wegen der Umstrukturierung
`cmd /k hostname` für PC Namen
