import factory

from backend.database_models import Group
from backend.tests.factories.base import BaseFactory


class GroupFactory(BaseFactory):
    class Meta:
        model = Group

    display_name = factory.Faker("name")
