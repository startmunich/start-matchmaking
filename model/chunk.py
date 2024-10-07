class Chunk:
    def __init__(self, text, startie_id):
        self.text = text
        self.startie_id = startie_id

    def __str__(self) -> str:
        return f"text:{self.text}, startie_id:{self.startie_id}"
