import factory

from backend.database_models import Organization

from .base import BaseFactory


class OrganizationFactory(BaseFactory):
    class Meta:
        model = Organization

    name = factory.Faker("company")
