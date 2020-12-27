from notification import Notification
from pullLastUpdates import archifPullLastUpdates
from sqliteConnection import *

conn = createConnection('notifications.db')
createTable(conn)


archif = archifPullLastUpdates()
importSource(conn, "meddl.center", archif)

