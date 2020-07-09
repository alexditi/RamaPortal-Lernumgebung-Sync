# RamaPortal Client-Sided Projects

Hier werden Projekte veröffentlicht, die die [RamaPortal Website](https://portal.rama-mainz.de "Zum RamaPortal") zugänglicher für den Desktop machen.

* Lernumgebung Offline Synchronisation
* Desktop Chat Funktion
* RamaPortal als Desktop Version

Unter Releases den neuesten Release downloaden und die .zip entpacken. In den jeweiligen Ordnern findet man die benötigten Dateien für das Projekt.

__ __

### Lernumgebung Offline Synchronisation

Ordner "Lernumgebung Sync"

**Wichtig:**

Aktuell gibt es nur die reine .py Datei für die Lernumgebung Synchronisation zum Download.

Um diese auszuführen, müssen folgende Schritte befolgt werden (Windows):

1. [Python Interpreter](https://www.python.org/downloads/ "Zum Python Download") herunterladen und ausführen
2. Checkbox "Add Python to PATH" auswählen
3. "Install Now" auswählen
4. CMD (Eingabeaufforderung) oder Powershell öffnen (Kann in der Windows Suche geöffnet werden)
5. Folgende 2 Befehle eingeben und ausführen:
   * `pip install beautifulsoup4`
   * `pip install requests`
6. Python sollte nun installiert  und die .py Datei per Doppelklick ausführbar sein

Für andere Betriebssysteme müssen Python sowie und die Zusatzbibliotheken `beautifulsoup4` und `requests` installiert
sein (ebenso über pip und die o.g. Befehle möglich)

Automatisches Ausführen des Skripts beim Startvorgang des Windows PCs:

Möchte man die Lernumgebung automatisch beim Start des PCs synchronisieren lassen, so wird zusätzlich die Datei "LU Sync Autostart.txt" benötigt:

1. Die Datei mit einem beliebigem Texteditor öffnen
2. Ganz unten in der Datei im Abschnitt `<Arguments>` muss nun `Pfad/zur/Datei/Lernumgebung Synchronisation.pyw` durch
den Pfad zur Datei "Lernumgebung Synchronisation.pyw" ersetzt werden. Der Pfad muss dabei in den
Anführungszeichen stehen bleiben.
3. Im Texteditor nun den Dialog "Speichern unter" aufrufen. Der Name der Datei bleibt erhalten, lediglich die Dateiendung (.txt)
wird durch .xml ersetzt. Nun sollte die Datei "LU Sync Autostart.xml" existieren. Die .txt Datei wird nicht mehr benötigt.
4. Aufgabenplanung öffnen (Kann über die Windows Suche geöffnet werden)
5. Rechts im Reiter Aktionen "Aufgabe importieren" auswählen
6. Die Datei "LU Sync Autostart.xml" öffnen
7. Den sich öffnenden Dialog mit "OK" bestätigen

Nun sollte nach der Anmeldung bei Windows das Skript gestartet werden. Nach Beendigung der Synchronisation kann das
Skript geschlossen werden.

__ __

### RamaPortal Client

Nicht ausgereifte Desktop Version des RamaPortals (**nicht funktionsfähig**)
