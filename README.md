# RamaPortal Client-Sided Projects

Hier werden Projekte veröffentlicht, die die [RamaPortal Website](https://portal.rama-mainz.de "Zum RamaPortal") zugänglicher für den Desktop machen.

* Lernumgebung Offline Synchronisation
* Desktop Chat Funktion
* RamaPortal als Desktop Version

Unter Releases den neuesten Release downloaden und die .zip entpacken. In den jeweiligen Ordnern findet man die benötigten Dateien für das Projekt.

__ __

### Lernumgebung Offline Synchronisation

Ordner "Lernumgebung Sync"

Für die Lernumgebung Offline Synchronisation ist für Windows 10 (64bit) eine .exe Datei vorhanden. Diese kann einfach benutzt und per Doppelklick ausgeführt werden.  
Die Datei LU_updater.exe ist die Update Datei der Lernumgebung Synchronisation und wird nicht benötigt. Sie ist nur in diesem Verzeichnis auf GitHub, damit sie, falls eine neue Version verfügbar ist, von dre Lernumgebung Synchronisation heruntergeladen werden kann und das Update selbstständig ausführt. Die LU_updater.exe Datei kann außerdem nicht ohne weiteres selbstständig ausgeführt werden.

Der Sourcecode ist auch erhältlich. Die Datei LernumgebungSynchronisation.pyw ist die Python Datei, die über eine gängige [Python Installation](https://www.python.org/downloads/ "Zum Python Download") ausgeführt werden kann. Zusätzlich müssen die beiden Module `requests` und `beautifulsoup4` installiert werden. Der Python Sourcecode läuft aktuell auch nur über Windows, da auf die Windows PATH-Variablen zugegriffen wird. (Auf anderweitigen Betriebssystemen wurde es zwar noch nicht getestet, es sollte aber eine Fehlermeldung auftreten). Auch für den Updater ist der Soucecode unter LU_updater.py vorhanden.  
Die beiden Module werden mithilfe von pip, einem in Python beinhalteten Installer für Python Module installiert werden. Dazu eine Konsole öffnen und die Befehle `pip install beatifulsoup4` und `pip install requests` ausführen.

Bei der ersten Ausführung der .exe Datei wird der Windows Defender wahrscheinlich das Ausführen blockieren. Um es zuzulassen, „weitere Informationen“ anklicken und dann „Trotzdem ausführen“ auswählen.

Wird die Lernumgebung Synchronisation zum ersten Mal gestartet, so müssen die benötigten Nutzerdaten angegeben werden. Das Passwortfeld ist sichtgeschützt, was aber mit dem Button neben der Eingabe geändert werden kann.  
Als Synchronisationspfad wird ein Überordner angegeben (mit dem Button neben der Eingabe den Windows Pfad Dialog öffnen). In dem ausgewählten Ordner wird ein weiterer Ordner, LU Synchronisation, erstellt, in den die Lernumgebung synchronisiert wird.

__ __

### RamaPortal Client

Ordner "RamaPortal Client"

Nicht ausgereifte Desktop Version des RamaPortals (**nicht funktionsfähig**)
