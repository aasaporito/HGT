class SequenceData:
    def __init__(self, sequence):
        self.sequence = sequence
        self.genomes = set()
        self.fragments = set()
        self.pairs = []

    def __repr__(self):
        return f"({self.sequence}, {self.genomes}, {self.fragments}, {self.pairs})"