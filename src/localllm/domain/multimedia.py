class Album:
    """Album is a class that represents an album in the multimedia library."""

    def __init__(self, album_id: str, title: str, artist: str, year: int):
        self.album_id = album_id
        self.title = title
        self.artist = artist
        self.year = year

    def __str__(self):
        return f"{self.title} by {self.artist} released in {self.year}"
