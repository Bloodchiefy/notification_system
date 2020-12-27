# Einführung

## Motivation

Ich wollte ein kleines Projekt starten. Ein kleines Benachrichtigungssystem, dass mir alle wichtigen Benachrichtungen gibt, die ich brauche. Dazu habe ich mir folgendes vorgestellt:
1. Eine kleine Anwendung geschrieben in Python, die die wichtigen Informationen sammelt.
2. Eine kleine Webanwendung (in Python mit Flask), die die Informationen schön darstellt und in meinem internen Netzwerk verfügbar sind.

Im internen Netzwerk benötige ich das nur, damit muss ich mich auch nicht mit Datensicherheit beschäftigen. Außerdem wollte ich die Anwendung so einfach wie möglich halten, um damit ein kleines Tutorial starten. Dieses Tutorial soll das Codeergebnis, was ich erstellt habe, successive erklären, meine Gedanken und meine Recherchen zu jedem Arbeitsschritt darstellen. Auf diese Weise kann man vielleicht mehr lernen, und ich mein Vorgehen besser reflektieren.

## Arbeitsschritte

### Datensammlung

Ich habe mir das so vorgestellt, dass ich die Datensammlung und die Datendarstellung trenne. Die Datensammlung soll wenn möglich APIs abrufen können, sowie aber auch aus Webseitendaten (HTML-Daten) die notwendigen Informationen extrahieren können. Hier ist ein kleines Beispiel vorgestellt anhand der Webseite "meddle.center":

Meine Idee war zuerst, dass man die gewünchten Informationen mit einem `curl`-Befehl holt, in eine Datei ablegt, den HTML-Text liest und sich daraus das Wichtigeste extrahieren lässt. Für die `curl`-Funktion in Python habe ich zuerst die Bibliothek `urllib.request` verwendet, jedoch hat sich herausgestellt, dass für meinen Anwendungszweck sich die Bibliothek `requests` besser eignet.

Dann musste ich mir überlegen, wie ich die Informationen abspeichere und im Arbeitsspeicher halte. Dafür habe ich eine Klasse erstellt namens `Notification`:

**project/notification.py**
```python
class Notification:
    def __init__(self, id, epoch, source, topic, description):
        self.id = id
        self.epoch = epoch
        self.source = source
        self.topic = topic
        self.description = description
```

Damit habe ich auch gleichzeitig die wichtigsten Attribute festgelegt, die ich für relevant halte:

- **id**: Wurde testweise erstellt, ist aber eigentlich nicht wichtig. Das soll ein integer sein, der von 0-29 (beides inklusive) geht und für jede Quelle (jede Webseite, von der ich benachrichtigt werden möchte) nur in diesem Bereich operiert. Ich möchte nur die 30 letzten Aktualisierungen von der Webseite erhalten, dies erspart mir Speicher und sollte genug Information sein.

- **epoch**: Soll den Zeitpunkt speichern, an dem die Benachrichtigung hinzugefügt wurde. Dies ist dann für die Sortierung der Benachrichtigungen wichtig.<br><br>

- **source**: Quelle der Benachrichtigung _(in unserem Beispiel das "meddl.center")_<br><br>

- **topic**: Soll den Titel der Benachrichtigung beinhalten _(in unserem Beispiel den Titel des Videos, den das `meddl.center` vergeben hat)_<br><br>

- **description**: Beschreibung der Benachrichtigung _(zum Beispiel den Titel des neu hochgeladenen Videos von unserem allseits beliebten Drachenlord)_<br><br>

Bevor wir mit dem Coden beginnen, sollte ich erklären, warum ich mich für die Repräsentation der Benachrichtigung als Klasse entschieden habe. Der Grund ist, dass ich somit leichter auf die Attribute einer Benachrichtigung zugreifen kann, ohne mich um Reihenfolgen der Attribute kümmern müsste. Hier ein kleines Codebeispiel, wie ich das mit Listen (ähnlich zu Arrays in java) machen kann.

```python
notification = (0, "2020-12-27 12:00:00.123093", "meddl.center", "Drachenlord Youtube 24.12.2020 #reupload [02:28:16h]", "Frohe Weinachten mit Marvins Mittens")

epoch = notification[1] # Holt den Zeitpunkt der Benachrichtigung
description = notification[4] # Holt die Beschreibung der Benachrichtigung
```

Hier ein kurzes Beispiel zum Aufruf, wenn ich die oben beschriebene Klasse hätte:

```python
notification = Notification(0, "2020-12-27 12:00:00.123093", "meddl.center", "Drachenlord Youtube 24.12.2020 #reupload [02:28:16h]", "Frohe Weinachten mit Marvins Mittens")

epoch = notification.epoch
description = notification.description
```

Wie man sehen kann, benötige ich im zweiten Beispiel keine Arrayklammern, und ich muss nicht zählen, auf welcher Position die gewünschte Information in der Liste steht. Nach einer kurzen Recherche zu [Klassen in Python](https://docs.python.org/3/tutorial/classes.html#class-definition-syntax) mache ich also folgendes:
1. Erstelle einen Ordner mit dem Namen des Projekts _(zum Beispiel "notificationSystem")_:
```sh
mkdir notificationSystem
```

2. Erstelle eine neue Datei in dem Ordner mit dem Namen `notification.py`:
```sh
cd notificationSystem
touch notification.py
```

3. Öffne die Datei mit einem Texteditor deiner Wahl (hier wird emacs verwendet) und schreibe den oben beschriebenen Code der Klasse in die Datei rein:

```sh
emacs notification.py &
```

In den &#60;Insert&#62;-Mode wechseln mit `i` und den Code von oben abtippen. \\
Dann speichern mit C-x C-s (Ctrl-x Ctrl-s).


Damit ist die erste Vorbereitung des Projektes erledigt. Normalerweise sollte man sich als nächstes mit der Speicherung der Daten beschäftigen, aber so habe ich es nicht gemacht, denn ich wollte zuerst ein bisschen rumprobieren, wie ich mit den HTML-Daten umgehen muss, die Informationen, die ich haben möchte rausziehen kann, und dann in Objekte meiner Klasse `Notification` umwandeln kann. Deshalb wird auch in diesem Tutorial so vorgegangen.

4. Deshalb erstellen wir nun eine neue python-Datei, in der wir die Methoden zur Datensammlung definieren. Wir nennen diese Datei "pullLastUpdates.py" und speichern diese im selben Ordner (dem Projekt-Ordner) ab:

```sh
touch pullLastUpdates.py
```

5. Öffnen der Datei in emacs:

`Zu emacs wechseln` -&#62; `F10` -&#62; `File` -&#62; `Open File` -&#62; `pullLastUpdates.py auswählen`.

6. Füllen der Datei:

Zuerst benötigen wir einen import für die oben erwähnte Bibliothek `requests`. Außerdem benötigen wir 3 weitere imports, nämlich unsere Klasse `Notification` aus unserer `notification.py`, ein Object `datetime` aus der Bibliothek `datetime` und eine Klasse `BeautifulSoup` aus der Bibliothek `bs4`. Um sicherzustellen, dass wir die Bibliothek haben, sollten wir auf die Konsole wechseln, und diese Bibliotheken installieren:
```sh
pip install requests --user
pip install bs4 --user
```

`pip` ist der Packageinstaller von Python und _(pip steht für `pip installs packages`)_ ist nicht nur das beste Meme, sondern installiert uns ein beschriebenes Packages, falls es noch nicht installiert ist und falls es das Package gibt. Die Bibliothek `datetime` muss normalerweise nicht installiert werden, weil diese meist standardmäßig bei der Python-Installation mit dabei ist. Der Flag `--user` bedeutet, dass das package für den aktuellen Nutzer installiert wird. Dies erspart uns root-Aufrufe mit `sudo` oder sonstige Berechtigungsprobleme. 

Nun können wir wieder zu emacs wechseln und zuerst folgenden Code einfügen:

```python
import requests

from notification import Notification
from datetime import datetime
from bs4 import BeautifulSoup
```

Nun definieren wir uns die Methode, die vom "meddl.center" die letzten Video-Uploads von der rainsten Drachenseele holt und verarbeitet. Dazu gehen wir kurz auf die Seite und schauen uns an, was uns genau interessiert. Mich hat zunächst nur die `archif`-Seite interessiert unter der URL `https://meddl.center/archif` zu finden. Wenn wir die Seite in Firefox geöffnet haben, können wir mal auf die Beschreibung eines Videos Rechtsklicken und `Inspect Element (Q)` auswählen. Man bekommt den HTML-Code angezeigt, und man kann dadurch folgendes rauslesen:

- Die Beschreibung befindet sich in einem &#60;i&#62;-Tag
  - dieser befindet sich wiederrum in einem &#60;a&#60;-Tag
    - dieser befindet sich wiederrum in einem &#60;li&#62;-Tag
      - dieser befindet sich wiederrum in einem &#60;ul&#62;-Tag

Der &#60;ul&#62;-Tag hat den Klassennamen (class=) `archif`, und ich vermutete, dass hier die unsortierte Liste der Videos abgespeichert waren. Sie war jedoch schon sortiert, was uns sehr viel Arbeit erspart.
Zum Überprüfen, ob es nur diese eine Liste gibt, gehen wir in Firefox zu der Console und tippen folgendes ein:

```js
$('.archif')
```

Wir bestätigen die Eingabe mit ENTER und sehen, dass Firefox nur ein Element zurückgibt.

Um in Python auf HTML Elemente zugreifen zu können habe ich im Internet gesucht, und bin erstmal auf diesen StackOverflow-Thread gestoßen: https://stackoverflow.com/questions/46938207/in-python-3-how-can-i-select-html-a-tag-text

Der zweite Kommentar unter der Frage hat mir eine gewisse Vorstellung davon gegeben, wie ich damit arbeiten soll, und dass mit die Bibliothek `BeautifulSoup` helfen könnte.

Dieser StackOverflow Thread hat auch geholfen um zu verstehen, wie ich durch html-Listen durchiterieren kann: https://stackoverflow.com/questions/44723713/python-beautifulsoup-iterating-through-tags-and-attributes


Nun aber wieder zum Code. Wir müssen uns den Inhalt der Seite holen und diesen am besten als String in eine Variable speichern. Dafür habe ich mir den zweiten Kommentar von diesem Thread angeschaut: https://stackoverflow.com/questions/65392491/python-curl-output-different-from-original-html

Obwohl dieser Kommentar einen Downvote hatte, damit konnte ich arbeiten. Wir wechseln wieder zu emacs und geben folgenden Code in die noch offene Datei ein:

```python
...
def archifPullLastUpdates():
    archifStr = requests.get("https://meddl.center/archif").content.decode("utf8")
```

`def archifPullLastUpdates():` ist die Definition unserer Methode. Sie benötigt keine Parameter.

Mit `requests.get("https://meddl.center/archif")` holen wir uns das HTTPS Paket vom meddl.center, der Aufruf `.content` liefert uns den Condend der Seite als HTML-String. Mit dem Aufruf `.decode(utf8)` wird der String mit der "utf8"-Characterbasis gelesen. Für andere Webseiten kann es erforderlich sein, dass wir eine andere Characterbasis benötigen. Wir weisen den String der Variablen `archifStr` zu.

Nun können wir den HTML-String in BeautifulSoup reinstecken und damit arbeiten. 

```python
...
def archifPullLastUpdates():
    ...
    soup = BeautifulSoup(archifStr, 'html.parser')
    ul = soup.select_one('ul.archif')

```

Wir rufen `BeautifulSoup` auf mit den Parametern `archifStr`, also unser gerade eben geholter HTML-String vom meddl.center, und `html.parser`, was der Klasse sagt, dass uns der geparste HTML-Code interessiert. Dies speichern wir in eine Variable `soup`. 

Nun können wir uns mithilfe der Methode `select_one()` und sogenannten CSS-Selektoren die Liste holen. Dies machen wir mit `soup.select_one('ul.archif')`. `ul.archif` ist ein CSS-Selektor, der folgendes aussagt: Selektiere die &#60;ul&#62;-Tags, die als Klassennamen (class=) `archif` haben. Nach unseren Nachforschungen gibt es da nur eine Liste, die uns zurückgegeben wird. Diese speichern wir in eine Variable `ul`.

Nun können wir unsere erste Benachrichtigungsliste zusammenbasteln:

```python
...
def archifPullLastUpdates():
    ...
    notificationArray = []
    counter = 0
    
    for li in ul:
        id = counter
        epoch = datetime.now()
        source = "meddl.center"
```

Wir initialisieren uns ein leeres Array namens `notificationArray` und eine Zählvariable namens `counter` mit 0 initialisiert. Dann können wir mit `for li in ul` durch die Liste `ul` durchgehen. `li` beinhaltet dabei immer das aktuelle Kindelement der Liste. Den Namen `li` habe ich deshalb gewählt, da die Listeneinträge in HTML-Listen mit &#60;li&#62;-Tags beschrieben sind. Die Variable kann aber auch anders heißen.

Dann initialisieren wir zuerst alle Attribute, die wir für die Klasse `Notification` benötigen. Wir benötigen `id`, das ist einfach unsere `counter`-Variable. Die `epoch` soll den aktuellen Zeitpunkt speichern, diesen bekommen wir durch den Aufruf `datetime.now()`. Unsere Quelle ist in unserem Beispiel das `meddl.center`, und darauf setzen wir eine Variable `source`.

Nun können wir uns aus dem aktuellen Element `li` das `topic` und die `description` herausholen. Für `topic` müssen wir uns nur alle &#60;a&#62;-Tags mit `li.findAll('a')` suchen, das erste Element herausholen und mit `.next` können wir auf die Linkbezeichnung zugreifen.

Für die Beschreibung (`description`) müssen wir uns aus mehreren Subelementen von li etwas herausholen. Damit wir keine Fehler bekommen, müssen wir immer überprüfen, ob das gewünschte Subelement existiert. 

Der Code dafür sieht wie folgt aus:

```python
...
def archifPullLastUpdates():
    ...
    for li in ul:
        ...
        topic = li.findAll('a')[0].next
        description = ""
        if len(li.findAll('a')) > 0:
            if len(li.findAll('a')[0].findAll('i')) > 0:
                description = li.findAll('a')[0].findAll('i')[0].next
```

Wir initialisieren `description` als leeren String, damit wir die Variable in der for-Schleife definiert haben, und sie noch in der for-Schleife verwenden können. Mit der ersten `if` schauen wir, ob das Listenelement überhaupt Links hat. `li.findAll('a')` gibt uns ein Array mit allen Links im &#60;li&#62;-Tag zurück, und wenn die Länge davon nicht größer 0 ist, dann besitzt dieser &#60;li&#62;-Tag keine Links. Als nächstes schauen wir, ob beim ersten (nullten) Link &#60;i&#62;-Tags drinnen sind. Das sind die Tags, die den Video-Titel von unserem lieben Kugli in kursiv darstellen, und den wir in unsere Benachrichtigung als `description` speichern wollen. Dies machen wir mit dem Ausdruck hier: `li.findAll('a')[0].findAll('i')`
Hier testen wir auch die Länge, dass diese größer 0 ist. Falls also ein Video einen Video-Titel besitzt, können wir auf das erste kursiv geschriebene Element zugreifen und mit `.next` holen wir uns den Text heraus.

Nun können wir unsere Benachrichtigung zusammenbauen und zu unserer Liste `notificationArray` hinzufügen:

```python
...
def archifPullLastUpdates():
    ...
    for li in ul:
        ...
        notificationArray.append(Notification(id, epoch, source, topic, description))
        counter += 1
        if counter > 29:
            break

```

Mit dem `Notification(id, epoch, source, topic, description)` initialisieren wir unsere Benachrichtigung und mit `notificationArray.append(...)` fügen wir unsere Benachrichtigung unserem Array hinzu. Unsere Zählvariable wird um 1 hochgezählt und wir überprüfen, ob diese größer 29 wird. Falls dies der Fall ist, wollen wir die Schleife abbrechen, um nicht mehr als 30 Element der Liste zu betrachten.

Als nächstes müssen wir leider nochmal das Array durchgehen und die Zeitstempel der Benachrichtigungen vertauschen. Wir sind jetzt durch die Liste vom ersten Eintrag in der Liste (dem zuletzt hinzugefügten Video) aus durchgegangen und haben diese mit einem eigenen Zeitstempel versehen. Somit ist aber der letzte Eintrag der Liste unser ältester Eintrag geworden, und eigentlich müsste es der jüngste sein. Deshalb gehe ich die Benachrichtigungen im `notificationArray` durch und vertausche das letzte Datum mit dem ersten, das vorletzte Datum mit die zweiten, das vorvorletzte Datum mit dem dritten, usw. Wir verwenden unsere Zählvariable `counter` einfach wieder und setzten diese zuerst auf 0.

```python
...
def archifPullLastUpdates
    ...
    counter = 0
    for notification in notificationArray:
        tmpEpoch = notificationArray[29 - counter].epoch
        notificationArray[29 - counter].epoch = notification.epoch
        notification.epoch = tmpEpoch
        counter += 1
        if counter == 15:
            break
    return notificationArray
```

In dem `tmpEpoch` speichern wir die Epoch vom `counter`-letzten Element in der Liste (dem Element, mit dem jüngsten / `counter`-ältesten Datum). Mit dem Aufruf `notificationArray[29 - counter]` bekommen wir im 0ten Schritt das letzte Element des Arrays zurückgegeben, im 1ten Schritt das 28te Element des Arrays, im 2ten Schritt das 27te, um 3ten Schritt das 26te, ..., im 13ten Schritt das 16te, im 14ten Schritt das 15te Element des Arrays. Dann können wir aufhören, der counter wird ein letztes mal von 14 auf 15 hochgezählt, und dann bricht unsere `if`-Bedingung unsere `for`-Schleife ab. Zurückgeben können wir dann unser `notificationArray**.

Nun sollte unser kompletter Code für diese Datei wie folgt aussehen:

**project/pullLastUpdates.py**
```python
import requests

from notification import Notification
from datetime import datetime
from bs4 import BeautifulSoup


def archifPullLastUpdates():
    archifStr = requests.get("https://meddl.center/archif").content.decode("utf8")

    soup = BeautifulSoup(archifStr, 'html.parser')
    ul = soup.select_one('ul.archif')

    notificationArray = []
    counter = 0
    for li in ul:
        id = counter
        epoch = datetime.now()
        source = "meddl.center"
        topic = li.findAll('a')[0].next
        description = ""
        if len(li.findAll('a')) > 0:
            if len(li.findAll('a')[0].findAll('i')) > 0:
                description = li.findAll('a')[0].findAll('i')[0].next
        notificationArray.append(Notification(id, epoch, source, topic, description))
        counter += 1
        if counter > 29:
            break

    counter = 0
    for notification in notificationArray:
        tmpEpoch = notificationArray[29 - counter].epoch
        notificationArray[29 - counter].epoch = notification.epoch
        notification.epoch = tmpEpoch
        counter += 1
        if counter == 15:
            break

    return notificationArray
```

Damit haben wir die Datensammlung vorerst abgeschlossen und wir können uns um die Speicherung kümmern.


### Speicherung der gesammelten Daten
Für die Speicherung der Daten habe ich mich für eine `sqlite3` Datenbank entschieden. Solche Datenbanken werden gerne auf Smartphones verwendet und bieten den Vorteil, dass sie ziemlich light-weight ist, für gewisse Anwendungen eine gute Performance bietet und ziemlich leicht zu implementieren ist. Man braucht keinen Datenbank-Server, der sqlite-Client, der vom Python-Programm aus gestartet wird stellt eigentlich nur eine Verbindung zu einer `.db`-Datei her. Für das Arbeiten mit sqlite3 in python habe ich mich erstmal kurz mit folgendem Artikel beschäftigt: https://www.tutorialspoint.com/python_data_access/python_sqlite_where_clause.htm

Zuerst müssen wir also eine Bibliothek installieren namens `sqlite3`:

```sh
pip install sqlite3 --user
```

Und wir legen schonmal eine neue Python-Datei an, wo wir den Code für die Speicherung haben wollen. Dies macht Sinn, da damit die Datensammlung und Datenspeicherung logisch getrennt werden, aber es ermöglich auch die Austauschbarkeit der jeweiligen Schicht. Man kann dies auch unter dem Begriff Seperation of Concerns fassen.

```sh
touch sqliteConnection.py
```

Folgende Vorüberlegung für diese Methoden fassen wir kurz zusammen:
- Eine Methode, die uns die Verbindung zu einer sqlite-Datenbank erstellt.<br><br>
- Eine Methode, die uns eine Benachrichtigungstabelle erstellt, falls diese noch nicht existiert _(beim ersten Aufruf vom Programm beispielsweise)_<br><br>
- Eine Methode, die uns alle Benachrichtigungen zurückgibt.<br><br>
- Eine Methode, die uns die Benachrichtigung von einer bestimmten Quelle zurückgibt.<br><br>
- Eine Methode, die uns eine Liste von Benachrichtigungen in die Tabelle schreibt _(hinzufügt)_<br><br>
- Eine Methode, die uns eine Liste von Benachrichtigungen aus unserer Tabelle löscht _(zum Löschen von alten Einträgen)_<br><br>
- Eine Methode, die den Import übernimmt und die Datensammlung mit der Datenspeicherung verbindet.<br><br>

1. Zuerst öffnen wir wieder die Datei in emacs:

`Zu emacs echseln` -&#62; `F10` -&#62; `File` -&#62; `Open File` -&#62; `sqliteConnection.py auswählen und öffnen`

2. Dann bearbeiten wir die Datei und importieren erstmal die wichtigen Bibliotheken.

```python
import sqlite3

from notification import Notification
```

Die Bibliothek `sqlite3` benötigen wir, damit wir vereinfacht eine Verbindung zu unserer sqlite-Datenbank aufbauen können und mit SQL-Befehlen die Daten und die Datenstrukturen manipulieren können.

3. Als Nächstes brauchen wir die Methode, die uns eine Verbindung zur sqlite-Datenbank aufbauen kann:

```python
...
def createConnection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn
```

Diese Methode bekommt als Parameter einen String, der den Namen der sqlite-Datenbank beinhaltet, bzw. den Namen der Datenbank-Datei _(in unserem Beispiel ist das die 'notification.db')_.

Dann intialisieren wir eine Variable namens `conn`, die dann unsere Verbindung beinhalten soll. In einem `try`-Block, wird mithilfe der Bibliothek `sqlite3` die Methode`.connect()` aufgerufen, um eine Verbindung herzustellen. Diese Methode gibt dann eine Verbindung zurück, und wir speichern dies in unserer Variablen `conn`. Falls ein `Error` passieren sollte, laden wir im `except`-Block und wir geben einfach den Fehler auf der Konsole aus. Wenn dieses Programm in einem Cron-Job beispielsweise läuft, also immer wiederholt wird, sollte diese Ausgabe dann in einer log-Datei des Betriebssystem landen _(bzw. in einer log-Datei des Cron-Jobs)_.

Wir geben dann unsere Variable `conn` zurück. Es ist wichtig, dass wir eine Verbindung zurückgeben, auch wenn sie `None` ist, damit wir später entscheiden können, ob wir alles andere ausführen wollen, wenn keine Verbindung existiert. Somit kann man gut Fehler vermeiden.

4. Dann können wir eine Methode zur Erstellung unserer Tabelle machen:

```python
...
def createTable(conn):
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='notifications';")
    rows = cur.fetchall()

    if(len(rows) > 0 and "notifications" in rows[0]):
        return
```

Erstmal erstellen wir uns mit der Verbindung, die wir als Parameter übergeben bekommen, einen Cursor: `cur = conn.cursor()` Mit diesem können wir gut SELECT-Aufrufe machen, wie in diesem Beispiel:
```sql
SELECT name FROM sqlite_master WHERE type='table' AND name='notifications';
```

Dies sagt uns, ob es schon eine Tabelle namens `notifications` gibt, und soll uns dann den Namen dieser Tabelle sagen, der natürlich auch `notifications` ist. (Info)[https://stackoverflow.com/questions/1601151/how-do-i-check-in-sqlite-whether-a-table-exists]
Mit `cur.fetchall()` führen wir das SQL-Statement aus und wir speichern diese Ausgabe in die Variable `rows`. Dann überprüfen wir in der `if`, ob die Länge der `rows` größer 0 ist, also die Anzahl der mit dem SQL-Statement gefundenen Tabellen größer 0 ist. Und wir überprüfen, ob der String, der im nullten Eintrag der `rows` steht dem String `notifications` entspricht. Falls dies zutrifft, muss die Tabelle nicht nochmal erstellt werden, und mit return bricht die Methode ab.

Falls die Tabelle noch nicht existiert, muss sie erst noch erstellt werden:

```
...
def createTable(conn):
    ...
    conn.execute('''
    CREATE TABLE notifications(
    id INTEGER,
    epoch NUMERIC,
    source TEXT,
    topic TEXT,
    description TEXT,
    PRIMARY KEY (source, topic)
    );
    ''')
```

Die Tabelle soll `notifications` haben, und bekommt die Attribute, die die Klasse `Notification` hat:

- **id**: Werte von 0-29 sind vom Typ INTEGER
- **epoch**: Zeitstempel sind in sqlite vom Typ NUMERIC
- **source**: Die Quelle _(unser `meddl.center`)_ sind als Zeichenkette in sqlite vom Typ TEXT
- **topic**: Das Topic ist auch eine Zeichenkette, also auch TEXT
- **description**: Die Beschreibung ist auch eine Zeichenkette, also auch TEXT

Als Primärschlüssel habe ich die `source` als auch das `topic` zusammen gewählt. Für den Fall, dass ein Topic von zwei unterschiedlichen Quellen gleich heißt, können sie im Bezug auf die Quelle noch unterschieden werden. Ich hoffe nicht, dass der Fall eintritt, dass das gleiche Topic von derselben Quelle zweimal kommt. In diesem Fall sollte man die `epoch` wahrscheinlich noch zum Primärschlüssel hinzufügen. Dieses SQL-Statement muss nun von der Verbindung (von der `conn`) ausgeführt werden, weil dies die Struktur der Datenbank ändert, oder auch weil dies ein sogenanntes DDL-Statement ist.  Für unsere Anwendung reicht das aber erstmal und wir können zur nächsten Methode gehen.

5. Erstelle die Methode, die die Benachrichtigungen holt:

```python
...
def selectNotifications(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM notifications;")

    rows = cur.fetchall()
```

Erstmal erstellen wir uns einen cursor und führen mit seiner Hilfe das folgende SELECT-Statement aus:`

```sql
SELECT * FROM notifications;
```

Damit holen wir uns alle Einträge der Tabelle `notifications`.

Mit `cur.fetchall()` holen wir uns wieder alle Einträge und wir speichern diese wieder in eine Variable `rows`. Wir erstellen uns nun ein (python-Dictionary)[https://www.w3schools.com/python/python_dictionaries.asp], bei dem wir als Schlüssel den Primärschlüssel des jeweiligen Eintrages haben _(also `source` und `topic` der jeweiligen Benachrichtigung)_ und als Wert die Benachrichtigung selbst. Das machen wir wie folte:

```python
...
def selectNotifications(conn):
    ...
    notificationsDict = {}
    for row in rows:
        notificationsDict[str(row[2]) + str(row[3])] = Notification(row[0], row[1], row[2], row[3], row[4])

    return notificationsDict
```

Als erstes initialisieren wir ein leeres Dictionary namens `notificationsDict`. Dann gehen wir mit einer `for`-Schleife durch alle Einträge `rows` durch.
In der Variablen `row` Steht jetzt eine Benachrichtigung. Anhand dem obigen CREATE-TABLE-Statement kann man sehen, in welcher Reihenfolge die Attribute der Benachrichtigung in der Variablen `row` stehen. Deshalb initialisieren wir uns eine neue Benachrichtigung so: `Notification(row[0], row[1], row[2], row[3], row[4])` mit folgender Information wir es ein bisschen klarer:

- `row[0]` entspricht `id`,
- `row[1]` entspricht `epoch`,
- `row[2]` entspricht `source`,
- `row[3]` entspricht `topic`,
- `row[4]` entspricht `description`

Diese neue Benachrichtigung weisen wir in unserem Dictionary einen Platz zu. Dafür bauen wir uns den Schlüssel nach, der aus der Kombination von `source` und `topic` entsteht. `str(row[2]) + str(row[3])` konvertiert uns die jeweiligen zu strings und verbindet sie dann durch nichts getrennt. Dies ist dann der Schlüssel für unsere Benachrichtigung und so können wir diese in unser Dictionary einfügen: `notificationsDict[str(row[2]) + str(row[3])] = Notification(row[0], row[1], row[2], row[3], row[4])`

Nachdem alle Benachrichtigungen so in das Dictionary eingefügt worden sind, wird dieses mit return zurückgegeben, um weiterverarbeitet zu werden.


6. Erstelle eine Methode, die die Benachrichtigungen einer bestimmten Quelle zurückgibt.

```python
...
def selectNotificationsBySource(conn, sourceName):
    cur = conn.cursor()
    cur.execute("SELECT * FROM notifications WHERE source='" + sourceName + "';")

    rows = cur.fetchall()
    notificationsDict = {}
    for row in rows:
        notificationsDict[str(row[2]) + str(row[3])] = Notification(row[0], row[1], row[2], row[3], row[4])

    return notificationsDict
```

Hier bekommen wir neben der Verbindung `conn` auch den Quell-Namen `sourceName`, nachdem wir unsere Einträge filtern müssen. Nachdem wir einen cursor erstellt haben, führen wir ein ähnliches SELECT-STATEMENT aus, bei dem wir noch ein WHERE benutzen, um nach `source` zu filtern. `source` muss dem `sourceName` entsprechen, damit der Eintrag ausgewählt werden kann.
Die Erstellung eines python-Dictionary und dem Hinzufügen der Einträge folgt analog zu der Methode `selectNotifications()`, die bereits oben beschrieben wurde.

7. Erstelle eine Methode, die eine gegebene Benachrichtigungsliste in die Datenbank einfügt.

```python
...
def writeNotifications(conn, notificationArray):
    cur = conn.cursor()

    for notification in notificationArray:
        cur.execute(" \
        INSERT INTO notifications( \
        id, epoch, source, topic, description) VALUES \
        (" + str(notification.id) + ", '"  + \
        str(notification.epoch) + "', '" + \
        notification.source + "', '" + \
        notification.topic + "', '" + \
        notification.description + "');")

    conn.commit()
```

Wir bekommen ein `notificationArray` als Parameter. Wir erstellen uns wieder einen cursor, und wir starten eine `for`-Schleife. Mit `for notification in notificationArray` gehen wir die Benachrichtigungen durch, und `notification` beinhaltet immer die aktuell betrachtete Benachrichtigung. Mit dem `INSERT INTO`-Statement fügen wir die Werte der Benachrichtigung einzelnd in die Tabelle ein. Durch das `conn.commit()` bestätigen wir unsere Änderungen und die Transaktionen werden ausgeführt _(oder unsereBenachrichtigungen werden hinzugefügt)_.

8. Erstelle eine Methode, die eine gegebene Benachrichtigungsliste aus der Datenbank löscht.

```python
...
def deleteOldNotifications(conn, notificationArray):
    cur = conn.cursor()

    for notification in notificationArray:
        cur.execute("DELETE FROM notifications WHERE source='" + notification.source * "' AND topic='" + notification.topic + "';")

    conn.commit()
```

Diese Methode wird benötigt, damit wir alte Benachrichtigungen wieder aus unserer Datenbank rauslöschen können. Wir bekommen wieder ein `notificationArray`, indem alle Benachrichtigungen stehen, die wir löschen wollen. Wir gehen wieder alle Benachrichtigungen mit einer `for`-Schleife durch und führen für jede Benachrichtigungen ein DELETE-Statement aus, wobei natürlich die `source` und das `topic` übereinstimmen muss, weil dies unser Primärschlüssel ist. Mit `conn.commit()` bestätigen wir unsere Änderungen.

9. Erstelle eine Methode, die von einer gegebenen Quelle die gegebenen Benachrichtigungen importiert.

```python
...
def importSource(conn, sourceName, notifications):
    
    oldNotifications = selectNotificationsBySource(conn, sourceName)
    notificationsToPush = []
    
    for notification in notifications:
        key = notification.source + notification.topic
        if key not in oldNotifications:
            notificationsToPush.append(notification)
```

Wir rufen unsere soeben definierte Methode `selectNotificationsBySource(conn, sourceName)` um die bereits existenten Benachrichtigungen in der Datenbank der gegebenen Quelle `sourceName` zu holen. Wir initialisieren uns eine leere Liste namens `notificationsToPush`. Wir gehen dann die übergebenen Benachrichtigungen `notifications` mit einer `for`-Schleife durch. Hierbei wollen wir überprüfen, ob die übergebenen Benachrichtigungen schon in der Datenbank vorhanden sind, oder nicht. Deshalb bauen wir uns wieder einen Schlüssel zusammen mit der `source` und dem `topic` der Benachrichtigung. Dies speichern wir in der Variablen `key`. Wenn der Schlüssel nicht in den alten Benachrichtigungen (in der `oldNotifications`) vorhanden ist, dann wird diese Benachrichtigung zu der Liste `notificationsToPush` hinzugefügt. Nun müssen wir diese noch zur Datenbank hinzufügen.

```python
...
def importSource(conn, sourceName, notification):
    ...
    if len(notificationsToPush) > 0:
        writeNotifications(conn, notificationsToPush)
        allNotificaations = selectNotificationBySource(conn, sourceName)
        allNotifications = sorted(allNotifications.values(), key=lambda x:x.epoch)
        oldNot = allNotifications[30:]
        deleteOldNotifications(conn, oldNot)
```

Wir müssen nur etwas hinzufügen, falls es neue Benachrichtigungen überhaupt gibt, deshalb überprüfen wir, ob die Länge der Liste `notificationsToPush` größer 0 ist (also mindestens 1). Dann fügen wir zuerst die Benachrichtigungen hinzu. Dann holen wir uns wieder alle Benachrichtigungen der gegebenen Quelle aus der Datenbank und speichern diese in der Variablen `allNotifications`. Dann sortieren wir erstmal die alten Benachrichtigungen nach ihrem Zeitstempel "(Sortieren von Listen)[https://stackoverflow.com/questions/3766633/how-to-sort-with-lambda-in-python]". Von dieser Liste werden die Benachrichtigungen genommen, die nach 30 Einträgen kommen. Dies sind dann ältere Benachrichtigungen als die 30 vor ihnen. Diese werden in der Variablen `oldNot` gespeichert, und mit dem Aufruf `deleteOldNotifications(conn, oldNot)** können wir diese nun entfernen.

Nochmal zur Kontrolle hier der Komplette Code der eben behandelten Datei:

**project/sqliteConnection.py**
```python
import sqlite3

from notification import Notification

def createConnection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn

def createTable(conn):
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='notifications';")
    rows = cur.fetchall()

    if(len(rows) > 0 and "notifications" in rows[0]):
        return

    conn.execute('''
    CREATE TABLE notifications(
    id INTEGER,
    epoch NUMERIC,
    source TEXT,
    topic TEXT,
    description TEXT,
    PRIMARY KEY (source, topic)
    );
    ''')

def selectNotifications(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM notifications;")

    rows = cur.fetchall()

    notificationsDict = {}
    for row in rows:
        notificationsDict[str(row[2]) + str(row[3])] = Notification(row[0], row[1], row[2], row[3], row[4])

    return notificationsDict

def selectNotificationsBySource(conn, sourceName):
    cur = conn.cursor()
    cur.execute("SELECT * FROM notifications WHERE source='" + sourceName + "';")

    rows = cur.fetchall()
    notificationsDict = {}
    for row in rows:
        notificationsDict[str(row[2]) + str(row[3])] = Notification(row[0], row[1], row[2], row[3], row[4])

    return notificationsDict


def writeNotifications(conn, notificationArray):
    cur = conn.cursor()

    for notification in notificationArray:
        cur.execute(" \
        INSERT INTO notifications( \
        id, epoch, source, topic, description) VALUES \
        (" + str(notification.id) + ", '"  + \
        str(notification.epoch) + "', '" + \
        notification.source + "', '" + \
        notification.topic + "', '" + \
        notification.description + "');")

    conn.commit()

def deleteOldNotifications(conn, notificationArray):
    cur = conn.cursor()

    for notification in notificationArray:
        cur.execute("DELETE FROM notifications WHERE source='" + notification.source * "' AND topic='" + notification.topic + "';")

    conn.commit()

def importSource(conn, sourceName, notifications):
    oldNotifications = selectNotificationsBySource(conn, sourceName)
    notificationsToPush = []
    for notification in notifications:
        key = notification.source + notification.topic
        if key not in oldNotifications:
            notificationsToPush.append(notification)

    if len(notificationsToPush) > 0:
        writeNotifications(conn, notificationsToPush)
        allNotificaations = selectNotificationBySource(conn, sourceName)
        allNotifications = sorted(allNotifications.values(), key=lambda x:x.epoch)
        oldNot = allNotifications[30:]
        deleteOldNotifications(conn, oldNot)
```

### Zusammensetzen und erstes Ausführen
Nun setzen wir alles zusammen und können es erstmal ausführen. Für ein regelmäßiges Update werden wir noch einen Cron-Job anlegen, damit beschäftigen wir uns aber erst später. Wir legen nun im Projekt-Ordner eine neue Datei an:

```sh
touch main.py
```

Nun füllen wir diese wieder mit Code:

`Zu emacs wechseln` -&#62; `F10` -&#62; `File` -&#62; `Open File` -&#62; `main.py auswählen und öffnen` (&#60;Insert&#62;-Modus nicht vergessen :sweat_smile:)

Zuerst müssen wir wieder etwas importieren, und zwar unsere Datensammlungs-Methode und 3 Methoden aus der Datenspeicherung:

```python
from pullLastUpdates import archifPullLastUpdates
from sqliteConnection import importSource, createConnection, createTable
```

Dann erstellen wir eine Verbindung zu erstellen eine Tabelle, falls noch keine existiert.

```python
...
conn = createConnection('notifications.db')
createTable(conn)
```

Nun können wir die Updates vom `meddl.center` holen und importieren. Das machen wir so:

```python
archif = archifPullLastUpdates()
importSource(conn, "meddl.center", archif)
```

Der gesamte Code dafür ist wie folgt:

**project/main.py**
```python
from pullLastUpdates import archifPullLastUpdates
from sqliteConnection import importSource, createConnection, createTable

conn = createConnection('notifications.db')
createTable(conn)


archif = archifPullLastUpdates()
importSource(conn, "meddl.center", archif)
```

Nun können wir unseren Code mal testen. Das machen wir, indem wir folgendes auf der Konsole ausführen:

```sh
python main.py
```

Es sollte zu keinen Fehlern kommen, wenn alles installiert wurde. Außerdem sollte nun eine `notification.db` in unserem Ordner angelegt worden sein. Damit ist zumindest ein Teil der in der Motivation angesprochenen Punkte realisiert worden und in den nächsten Abschnitten kümmern wir uns um die Darstellung unserer Daten.

### Flask Anwendung
Wir wollen nun unsere Daten darstellen. Dazu können wir die Bibliothek `flask` verwenden, um einen kleinen Webserver zu starten, auf den wir im lokalen Netz zugreifen können.

Für die Basis, wie man eine kleine Flask-Anwendung schreibt, hilf mir diese Recherche: https://code-maven.com/a-polling-station-with-flask

Wir gehen aber hier auch Schritt für Schritt vor. Zunächst benötigen wir eine python Datei, die unseren Webserver repräsentiert. Zuerst installieren wir aber noch `flask`:

```sh
pip install flask --user
```

Jetzt legen wir in unserem Projektordner eine Python-Datei an, die `poll.py` heißen soll:

`Zu emacs wechseln` -&#62; `F10` -&#62; `File` -&#62; `Visit New File` -&#62; `main.py eingeben und ENTER`

Nun importieren wir von Flask etwas, und von unseren geschriebenen Klassen etwas, und die Bibliothek `os`:

```python
from flask import Flask, render_template
from sqliteConnection import createConnection, selectNotifications
from notification import Notification
import os
```

Wir erstellen nun den Flask server mit folgendem Aufruf:

```python
...
app = Flask(__name__)
```

Nun erstellen wir zwei Methoden. Eine Methode, die uns einfach eine Webseite zurückgibt, und eine weitere, die uns die Benachrichtigungen aus unserer Datenbank holt.

```python
...
@app.route('/')
def root():
    return render_template('poll.html')
```

Diese Methode sendet dem Client, der die Webseite anfrägt, einfach eine HTML-Datei. Die HTML-Datei wird `poll.html` heißen, und wir werden uns später mit der Bearbeitung davon beschäftigen. Nun fehlt noch die Methode, die unsere Benachrichtigungen als HTML zurückgibt. Dafür definieren wir diese Methode:

```python
...
@app.route('/notifications')
def notifications():
    conn = createConnection("notifications.db")
    notifications = selectNotifications(conn)
    notifyArray = []
    for key in notifications:
        notifyArray.append(notifications[key])

    notifyArray = sorted(notifyArray, key=lambda x: x.epoch, reverse=True)
    notifications = []
    for notification in notifyArray:
        notifications.append(( \
                notification.id, \
                notification.epoch, \
                notification.source, \
                notification.topic, \
                notification.description))


    return render_template('notifications.html', data=notifications)
```

Diese Methode erstellt zunächst eine Verbindung zu unserer sqlite-Datenbank, holt alle Benachrichtigungen und speichert diese mit der `for`-Schleife in `notifyArray`. Das müssen wir leider so machen, weil unsere Methode `selectNotifications()` ein Dictionary zurückgibt, und wir wollen aber eine Liste haben. Nun können wir diese Liste nach dem Datum sortieren. Dann müssen wir mit einer `for`-Schleife wieder durch die Liste durchgehen und aus den Benachrichtigungen arrays machen, damit unsere HTML-Seite, bzw. dann unser Javascript-Code damit umgehen kann. Dazu fügen wir zu der Liste `notifications` ein Tupel mit allen Attributen der `notification` hinzu. Dann wird eine HTML-Seite zurückgegeben, die aber noch als `data` die Benachrichtigungen bekommt. Diese HTML-Seite heißt `notifications.html`, die wir auch noch behandeln werden.

Zum Schluss müssen wir noch die Anwendung laufen lassen. Das machen wir mit folgendem Code:

```python
if __name__ == "__main__":
    app.run(debug=True)
``**

Hier nochmal der komplette Code:

**project/poll.py**
```python
from flask import Flask, render_template
from sqliteConnection import createConnection, selectNotifications
from notification import Notification
import os

app = Flask(__name__)


@app.route('/')
def root():
   return render_template('poll.html')

@app.route('/notifications')
def notifications():
    conn = createConnection("notifications.db")
    notifications = selectNotifications(conn)
    notifyArray = []
    for key in notifications:
        notifyArray.append(notifications[key])

    notifyArray = sorted(notifyArray, key=lambda x: x.epoch, reverse=True)
    notifications = []
    for notification in notifyArray:
        notifications.append(( \
                notification.id, \
                notification.epoch, \
                notification.source, \
                notification.topic, \
                notification.description))


    return render_template('notifications.html', data=notifications)

if __name__ == "__main__":
    app.run(debug=True)
```

Okay, wunderbar, jetzt können wir eine uns um die HTML-Seiten kümmern.
Dafür müssen wir zuerst einen neuen Ordner erstellen, den wir `templates` nennen:

```sh
mkdir templates
```

Nun wecheseln wir den Ordner und legen zwei Dateien an:

```sh
cd templates
touch poll.html
touch notification.html
```


Nun wechseln wir zu emacs und bearbeiten die erste HTML-Datei:
`Zu emacs wechseln` -&#62; `F10` -&#62; `File` -&#62; `Open File` -&#62; `templates/poll.html eingeben und ENTER drücken`

In dieser Datei schreiben wir zuerst einen Basis HTML-Code rein:

```html
<!DOCTYPE html>
<html>
    <head>
        <title>Newsticker</title>
    </head>
    <body>
        <h1>Newsticker</h1>
        <div id="notifications"></div>
    </body>
</html>
```

Nun wechseln wir wieder zur Konsole, wechseln wieder in dern Projekt-Ordner, erstellen einen neuen Ordner `static` und wechseln in diesen. Dann laden wir eine javascript-Datei runter, die uns erlaubt, jQuery-Code zu schreiben und Basis-Funktionen zu nutzen.

```sh
cd ..
cd static
curl https://code.jquery.com/jquery-3.5.1.min.js -o jquery.min.js
```

Jetzt wechseln wir wieder zu emacs und bearbeiten unsere `poll.html`. Wir müssen hier unsere neue `jquery.min.js** einbinden und ein bisschen Javascript schreiben, der immer wieder Anfragen an unseren Server schickt, der uns die Benachrichtigungen als HTML liefert, welches wir dann in unser HTML einbinden können. Dies folgt dem Code von dieser Seite: https://javascript.info/long-polling

**project/templates/poll.html**
```html
<!DOCTYPE html>
<html>
    <head>
        <title>Newsticker</title>
        <script type="text/javascript" href="{{ url_for('static', filename='jquery.min.js') }}"
        <script>
            async function subscribe() {
                let response = await fetch("/notifications");

                if(response.status == 502) {
                    await subscribe();
                } else if(response.status != 200) {
                    $("#notifications").html("<b>Daten momentan nicht verfügbar</b>");

                    await new Promise(resolve => setTimeout(resolve, 1000));
                    await subscribe();
                } else {
                    let message = await response.text();
                    $("#notifications").html(message);

                    await subscribe();
                }
            }

         subscribe();
        </script>
    </head>
    <body>
        <h1>Newsticker</h1>
        <div id="notifications"></div>
    </body>
</html>   
```

Nun öffnen wir die `notifications.html` in emacs und machen dort unsere finale Bearbeitung:

`Zu emacs wechseln` -&#62; `F10` -&#62; `File` -&#62; `Open File` -&#62; `templates/notifications.html eingeben und ENTER drücken`

In der `notifications.html** definieren wir, wie die Benachrichtigungen uns dargestellt werden sollen.

**projekt/notifications.html**
```html
<table>
    {% for e in data %}
    <tr>
        <td>{{ e[3] }}</td>
        <td>{{ e[2] }}</td>
        <td>{{ e[1] }}</td>
        <td>{{ e[4] }}</td>
    </tr>
    {% endfor %}
</table>
```

Wir wollen die Benachrichtigungen hier als Tabelle Darstellen. Dafür verwenden wir erstmal den &#60;table&#62;-Tag und öffnen hier eine `for`-Schleife, welches in einer Flaskanwendung richtig interpretiert wird. Wir gehen hier durch unser `data` durch, was wir von unserer `poll.py` in der Methode `notifications()` bekommen. Dann öffnen wir einen &#60;tr&#62;-Tag (Zeilen-Tag) und dann unseren ersten &#60;td&#62;-Tag (Spalten-Tag). Dort soll mir als erstes das `topic` der Benachrichtigung ausgegeben werden. Da nun `e` ein Array ist, müssen wir jetzt wieder nach Position des Attributes gehen, in unserem Fall hat das `topic` die dritte Position im Array. Deshalb schreiben wir `{{ e[3] }}` und danach den End-Tag der Spalte &#60;/td&#62;-Tag. So gehen wir für 3 weitere Attribute vor, der Quelle (zweite Spalte), dem Zeitstempel (dritte Spalte) und der Beschreibung (fünfte Spalte). Dann schließen wir die Zeile mit einem &#60;/td&#62;`-Tag und wir schließen die `for`-Schleife. Ganz zum Schluss verwenden wir noch den End-Tag der Tabelle, den &#60;/table&#62;-Tag.

Damit ist unser kleiner Server erstmal fertig. Wir starten die Anwendung, vom Projekt-Ordner aus, mit:

```
python poll.py
```

Nun können wir in einem Browser in die Adresszeile "localhost:5000" eingeben, und die Seite betrachten. Wir können währenddessen die `main.py` aufrufen und dadurch unsere Datenbank ändern, wenn unser kuglige Mitarbeiter mal wieder etwas hochlädt, und wir sehen das Ergebnis sofort, ohne das wir die Seite aktualisieren müssen.

Kleiner Kontrollblick noch, wenn wir alles richtig gemacht haben, sollte unsere Dateistruktur bezüglich unseres Projekt-Ordner wie folgt aussehen:

```
notificationSystem (unser Projektordner)
|    main.py
|    notification.py
|    notifications.db (falls das Programm schonmal ausgeführt wurde)
|    poll.py
|    pullLastUpdates.py
|    sqliteConnection.py
|
└----static
|        jquery.min.js
|
└----templates
         notifications.html
         poll.html
```

Das wäre zunächst das Ende dieses kleinen Tutorials, ich werde das Projekt noch selbst erweitern, und wenn ich Lust habe, schreibe ich noch an diesem Tutorial weiter. Aber damit wäre zumindest die "Basis" geschaffen, ich hoffe, manchen hilft das, besser ins Programmieren reinzukommen und sich mit wenig Arbeit trotzdem ein nützliches System zu basteln. Ich hoffe, die Wall of Text erschrickt nicht, und stellt die Komplexität vollkommen anders dar.

Viel Spaß und viel Erfolg!
