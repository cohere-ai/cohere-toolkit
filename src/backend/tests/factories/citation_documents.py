import factory

from backend.database_models import CitationDocuments

from .base import BaseFactory


class CitationDocumentsFactory(BaseFactory):
    class Meta:
        model = CitationDocuments

    left_id = factory.Faker("uuid4")
    right_id = factory.Faker("uuid4")
