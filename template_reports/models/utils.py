from django.conf import settings
from django.core.files.storage import storages


def get_storage():
    storage_key = getattr(settings, "TEMPLATE_REPORTS_STORAGE_KEY", None)
    if storage_key:
        return storages[storage_key]

    # Use default storage. (FileField rejects a storage callable returning
    # None, so the fallback must resolve the alias explicitly.)
    return storages["default"]
