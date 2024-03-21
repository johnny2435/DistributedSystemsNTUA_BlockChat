class Blockchain:
    def __init__(self, capacity):
        self.blocks = []

    def add_block(self, block):
        self.blocks.append(block)
        return
    
    def to_dict(self):
        data = {
            'blocks' : [x.to_dict() for x in self.blocks]
        }
        return data