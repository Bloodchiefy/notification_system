from pullLastUpdates import archifPullLastUpdates
from sqliteConnection import importSource, createConnection, createTable

conn = createConnection('notifications.db')
createTable(conn)


archif = archifPullLastUpdates()
importSource(conn, "meddl.center", archif)

