class Blockchain:
  def __init__(self):
      self.blocks = []

  def add_block(self, block):
      self.blocks.append(block)
      return

  def get_last_block(self):
      return self.blocks[-1]

  def to_dict(self):
      data = {
          'blocks' : [x.to_dict() for x in self.blocks]
      }
      return data
