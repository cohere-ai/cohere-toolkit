from uuid import uuid4

import factory


class BaseFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Always inherit from here"""

    class Meta:
        abstract = True  # Cannot initialize
        sqlalchemy_session = None
        sqlalchemy_session_persistence = "flush"

    id = factory.LazyFunction(lambda: str(uuid4()))
    created_at = factory.Faker("date_time")
    updated_at = factory.Faker("date_time")
