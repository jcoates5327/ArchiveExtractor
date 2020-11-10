class GravelAuthor:
    
    def __init__(self, name, url):
        self.name = name
        self.url = url


class GravelGenre:

    def __init__(self, name):
        self.name = name
        self.entries = []

    def add_entry(self, entry):
        self.entries.append(entry)

    def add_entries(self, entries):
        for entry in entries:
            self.entries.append(entry)