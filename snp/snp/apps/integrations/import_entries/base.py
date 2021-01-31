from abc import ABCMeta, abstractmethod

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from apps.core.models import Entry, Title
from ..exceptions import IntegrationError


class BaseImportAdapter(metaclass=ABCMeta):
    # We are trying to not to hold anything in the memory, this class is trying to just run everything at once
    # Since we are going to mostly write 2 *required* methods in the subclasses this shouldn't create much of a hassle
    # These should end up in task queues and should NEVER run on the application threads,even if we increase the
    # performance of these below, it is A LOT of network connections, we connect to a remote and write to our db heavily
    # We should also create a subclass hook to add the subclasses into a map at BaseImportAdapter.adapters_available
    # So that we can reference them at something like celery beat for the future scheduled jobs that we'll create for
    # the users whom wants to sync as they write, instead of letting them sync manually.
    @classmethod
    @abstractmethod
    def get_entries(cls, user, username):  # Should be a generator, otherwise oh boy...
        ...

    @classmethod
    def create_entries(cls, user, username):
        for entry in cls.get_entries(user, username):
            title = Title.objects.get_or_create(name=entry.pop('title__name'))
            Entry.objects.create(**entry, title=title)

    @classmethod
    def sync_online(cls, user, token, username):
        if user.verify_token(token, username):
            return cls.create_entries(user, username)

    @classmethod
    def sync_backup(cls, backup):
        if hasattr(cls, '_sync_backup_json'):
            return cls._sync_backup_json(backup)
        elif hasattr(cls, '_sync_backup_xml'):
            return cls._sync_backup_xml(backup)
        raise IntegrationError("We can only sync xml and json format backups for now.")

    @classmethod
    def _get_driver(cls):
        chrome_options = Options()
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")  # linux only
        chrome_options.add_argument("--headless")
        chrome_options.headless = True  # also works
        return webdriver.Chrome(options=chrome_options)
