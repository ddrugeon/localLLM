class Album:
    """
    Album is a class that represents a music album in the multimedia library.

    Attributes:
    - album_id: str, a unique identifier for the album
    - title: str, the title of the album
    - artist: str, the artist of the album
    - year: int, the year the album was released
    """

    def __init__(self, album_id: str, title: str, artist: str, year: int):
        self.album_id = album_id
        self.title = title
        self.artist = artist
        self.year = year

    def __str__(self):
        return f"{self.title} by {self.artist} released in {self.year}"
