class DraftController:
    is_draft = True

    def __init__(self, instance):
        self.instance = instance

    def select(self):
        if not self.is_draft:
            return self.instance.published
        return self.instance


class PublishedContextManager:
    def __enter__(self):
        DraftController.is_draft = False

    def __exit__(self, *args):
        self.is_draft = True
        DraftController.is_draft = True
