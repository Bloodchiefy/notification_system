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
    cur.execute("SELECT * FROM notifications")

    rows = cur.fetchall()

    notificationsDict = {}
    for row in rows:
        notificationsDict[str(row[2]) + str(row[3])] = Notification(row[0], row[1], row[2], row[3], row[4])

    return notificationsDict

def selectNotificationsBySource(conn, sourceName):
    cur = conn.cursor()
    cur.execute("SELECT * FROM notifications WHERE source='" + sourceName + "'")

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
        sortedNotifications = sorted(oldNotifications.values(), key=lambda x:x.epoch)
        oldNot = sortedNotifications[30:]
        deleteOldNotifications(conn, oldNot)
        writeNotifications(conn, notificationsToPush)


