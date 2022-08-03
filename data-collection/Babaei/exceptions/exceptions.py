
class ChannelDoesNotExistException(Exception):
    def __init__(self, channel_name) -> None:
        super().__init__(f'"{channel_name}" is not a valid channel in Telewebion')