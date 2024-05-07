import factory

from backend.database_models import User

from .base import BaseFactory


class UserFactory(BaseFactory):
    class Meta:
        model = User

    fullname = factory.Faker("name")
    email = factory.Faker("email")
