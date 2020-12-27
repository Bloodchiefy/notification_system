class Notification:
    def __init__(self, id, epoch, source, topic, description):
        self.id = id
        self.epoch = epoch
        self.source = source
        self.topic = topic
        self.description = description
