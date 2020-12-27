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

- id: Wurde testweise erstellt, ist aber eigentlich nicht wichtig. Das soll ein integer sein, der von 0-29 (beides inklusive) geht und für jede Quelle (jede Webseite, von der ich benachrichtigt werden möchte) nur in diesem Bereich operiert. Ich möchte nur die 30 letzten Aktualisierungen von der Webseite erhalten, dies erspart mir Speicher und sollte genug Information sein.

- epoch: Soll den Zeitpunkt speichern, an dem die Benachrichtigung hinzugefügt wurde. Dies ist dann für die Sortierung der Benachrichtigungen wichtig.<br><br>

- source: Quelle der Benachrichtigung _(in unserem Beispiel das "meddl.center")_<br><br>

- topic: Soll den Titel der Benachrichtigung beinhalten _(in unserem Beispiel den Titel des Videos, den das `meddl.center` vergeben hat)_<br><br>

- description: Beschreibung der Benachrichtigung _(zum Beispiel den Titel des neu hochgeladenen Videos von unserem allseits beliebten Drachenlord)_<br><br>

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
1. Eine Methode, die uns die Verbindung zu einer sqlite-Datenbank erstellt.
2. Eine Methode, die uns eine Benachrichtigungstabelle erstellt, falls diese noch nicht existiert _(beim ersten Aufruf vom Programm beispielsweise)_
3. Eine Methode, die uns alle Benachrichtigungen zurückgibt.
4. Eine Methode, die uns die Benachrichtigung von einer bestimmten Quelle zurückgibt.
5. Eine Methode, die uns eine Liste von Benachrichtigungen in die Tabelle schreibt _(hinzufügt)_
6. Eine Methode, die uns eine Liste von Benachrichtigungen aus unserer Tabelle löscht _(zum Löschen von alten Einträgen)_
7. Eine Methode, die den Import übernimmt und die Datensammlung mit der Datenspeicherung verbindet.


