from flask import Flask, render_template
from sqliteConnection import createConnection, selectNotifications
from notification import Notification
import os
app = Flask(__name__)

poll_data = {
    'question': 'Which web framework do you use?',
    'fields': ['Flask', 'Django', 'TurboGears', 'web2py', 'pylonsproject']
}

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
