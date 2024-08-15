import factory

from backend.database_models import Blacklist

from .base import BaseFactory


class BlacklistFactory(BaseFactory):
    class Meta:
        model = Blacklist

    token_id = factory.Faker("uuid4")
