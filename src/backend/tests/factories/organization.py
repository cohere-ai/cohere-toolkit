import factory

from backend.database_models import Organization
from backend.tests.factories.base import BaseFactory


class OrganizationFactory(BaseFactory):
    class Meta:
        model = Organization

    name = factory.Faker("name")
