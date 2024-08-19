import factory

from backend.database_models import Group

from .base import BaseFactory


class GroupFactory(BaseFactory):
    class Meta:
        model = Group

    display_name = factory.Faker("name")
