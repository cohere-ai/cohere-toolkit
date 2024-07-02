import factory

from backend.database_models import Snapshot, SnapshotAccess, SnapshotLink

from .base import BaseFactory


# Snapshot
class SnapshotFactory(BaseFactory):
    class Meta:
        model = Snapshot

    user_id = factory.Faker("uuid4")
    organization_id = factory.Faker("uuid4")
    conversation_id = factory.Faker("uuid4")
    last_message_id = factory.Faker("uuid4")
    version = factory.Faker("random_int")
    created_at = factory.Faker("date_time")
    updated_at = factory.Faker("date_time")
    snapshot = factory.Faker("pydict", value_types=[str, int, bool], nb_elements=10)


# SnapshotLink
class SnapshotLinkFactory(BaseFactory):
    class Meta:
        model = SnapshotLink

    snapshot_id = factory.Faker("uuid4")
    user_id = factory.Faker("uuid4")


# SnapshotAccess
class SnapshotAccessFactory(BaseFactory):
    class Meta:
        model = SnapshotAccess

    user_id = factory.Faker("uuid4")
    snapshot_id = factory.Faker("uuid4")
    link_id = factory.Faker("uuid4")
