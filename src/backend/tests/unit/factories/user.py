import factory

from backend.database_models import User
from backend.services.auth import BasicAuthentication

from .base import BaseFactory


class UserFactory(BaseFactory):
    class Meta:
        model = User
        exclude = "password"

    fullname = factory.Faker("name")
    email = factory.Faker("email")
    password = factory.Faker("password")
    hashed_password = factory.LazyAttribute(
        lambda o: BasicAuthentication.hash_and_salt_password(o.password)
    )

    # def _create(self, *args, **kwargs):
    #     password = kwargs.pop("password", None)
    #     if not password:
    #         fake = faker.Faker()
    #         password = fake.password()

    #     kwargs["hashed_password"] = BasicAuthentication.hash_and_salt_password(password)

    #     user = super._create(*args, **kwargs)

    #     return user
