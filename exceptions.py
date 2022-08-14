class SheetIdNotFoundException(Exception):
    def __init__(self, message='Sheet ID is not provided.'):
        self.message = message
        super().__init__(self.message)
