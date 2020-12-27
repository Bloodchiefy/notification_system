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



