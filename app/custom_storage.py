from django.core.files.storage import Storage

class NoStorage(Storage):
    def _open(self, name, mode='rb'):
        raise NotImplementedError("Storage backend is disabled")

    def _save(self, name, content):
        raise NotImplementedError("Storage backend is disabled")