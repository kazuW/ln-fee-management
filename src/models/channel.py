class Channel:
    def __init__(self, id, channel_name, channel_id, channel_point, capacity):
        self.id = id
        self.channel_name = channel_name
        self.channel_id = channel_id
        self.channel_point = channel_point
        self.capacity = capacity

    def __repr__(self):
        return f"Channel(id={self.id}, channel_name='{self.channel_name}', channel_id='{self.channel_id}', capacity={self.capacity})"