import pytest

from backend.crud import organization as organization_crud
from backend.database_models.organization import Organization
from backend.schemas.organization import UpdateOrganization
from backend.tests.factories import get_factory


def test_create_organization(session):
    organization_data = Organization(
        name="Test Organization",
    )

    organization = organization_crud.create_organization(session, organization_data)
    assert organization.name == organization_data.name

    organization = organization_crud.get_organization(session, organization.id)
    assert organization.name == organization_data.name


def test_get_organization(session):
    _ = get_factory("Organization", session).create(id="1", name="Test Organization")

    organization = organization_crud.get_organization(session, "1")
    assert organization.name == "Test Organization"


def test_fail_get_nonexistent_organization(session):
    organization = organization_crud.get_organization(session, "123")
    assert organization is None


def test_list_organizations(session):
    # Delete default organization
    session.query(Organization).delete()
    _ = get_factory("Organization", session).create(name="Test Organization")

    organizations = organization_crud.get_organizations(session)
    assert len(organizations) == 1
    assert organizations[0].name == "Test Organization"


def test_list_organizations_empty(session):
    # Delete default organization
    session.query(Organization).delete()
    organizations = organization_crud.get_organizations(session)
    assert len(organizations) == 0


def test_list_organizations_with_pagination(session):
    # Delete default organization
    session.query(Organization).delete()
    for i in range(10):
        _ = get_factory("Organization", session).create(name=f"Test Organization {i}")

    organizations = organization_crud.get_organizations(session, offset=5, limit=5)
    assert len(organizations) == 5

    for i, organization in enumerate(organizations):
        assert organization.name == f"Test Organization {i + 5}"


def test_list_organizations_by_user_id(session):
    organization = get_factory("Organization", session).create(name="Test Organization")
    user = get_factory("User", session).create()
    user.organizations.append(organization)

    organizations = organization_crud.get_organizations_by_user_id(session, user.id)
    assert len(organizations) == 1
    assert organizations[0].name == "Test Organization"


def test_list_organizations_by_user_id_empty(session):
    user = get_factory("User", session).create()

    organizations = organization_crud.get_organizations_by_user_id(session, user.id)
    assert len(organizations) == 0


def test_list_organizations_by_user_id_with_pagination(session):
    # Delete default organization
    session.query(Organization).delete()
    user = get_factory("User", session).create()
    for i in range(10):
        organization = get_factory("Organization", session).create(
            name=f"Test Organization {i}"
        )
        user.organizations.append(organization)

    organizations = organization_crud.get_organizations_by_user_id(
        session, user.id, offset=5, limit=5
    )
    assert len(organizations) == 5

    for i, organization in enumerate(organizations):
        assert organization.name == f"Test Organization {i + 5}"


def test_update_organization(session):
    organization = get_factory("Organization", session).create(name="John Doe")

    new_organization_data = UpdateOrganization(name="Jane Doe")

    updated_organization = organization_crud.update_organization(
        session, organization, new_organization_data
    )
    assert updated_organization.name == new_organization_data.name

    organization = organization_crud.get_organization(session, organization.id)
    assert organization.name == new_organization_data.name


def test_update_organization_partial(session):
    organization = get_factory("Organization", session).create(
        name="Test Organization U"
    )

    new_organization_data = UpdateOrganization(
        name="Test Organization U",
    )

    updated_organization = organization_crud.update_organization(
        session, organization, new_organization_data
    )
    assert updated_organization.name == new_organization_data.name


def test_donot_update_organization(session):
    organization = get_factory("Organization", session).create(name="Test Organization")

    new_organization_data = UpdateOrganization(name="Test Organization")

    updated_organization = organization_crud.update_organization(
        session, organization, new_organization_data
    )
    assert updated_organization.name == organization.name


def test_delete_organization(session):
    organization = get_factory("Organization", session).create()

    organization_crud.delete_organization(session, organization.id)

    organization = organization_crud.get_organization(session, organization.id)
    assert organization is None


def test_delete_nonexistent_organization(session):
    organization_crud.delete_organization(session, "123")  # no error
    organization = organization_crud.get_organization(session, "123")
    assert organization is None


def test_add_user_to_organization(session):
    organization = get_factory("Organization", session).create()
    user = get_factory("User", session).create()

    organization_crud.add_user_to_organization(session, user.id, organization.id)

    organization = organization_crud.get_organization(session, organization.id)
    assert user in organization.users


def test_remove_user_from_organization(session):
    organization = get_factory("Organization", session).create()
    user = get_factory("User", session).create()
    organization.users.append(user)
    organization_crud.remove_user_from_organization(session, user.id, organization.id)
    organization = organization_crud.get_organization(session, organization.id)
    assert user not in organization.users


def test_add_non_existent_user_to_organization(session):
    organization = get_factory("Organization", session).create()
    with pytest.raises(Exception):
        organization_crud.add_user_to_organization(session, "123", organization.id)


def test_remove_non_existent_user_from_organization(session):
    organization = get_factory("Organization", session).create()

    organization_crud.remove_user_from_organization(
        session, "123", organization.id
    )  # no error

    organization = organization_crud.get_organization(session, organization.id)
    assert len(organization.users) == 0


def test_get_users_by_organization_id(session):
    organization = get_factory("Organization", session).create()
    user = get_factory("User", session).create()

    organization.users.append(user)

    users = organization_crud.get_users_by_organization_id(session, organization.id)
    assert len(users) == 1
    assert users[0].id == user.id


def test_add_user_to_non_existent_organization(session):
    user = get_factory("User", session).create()
    with pytest.raises(Exception):
        organization_crud.add_user_to_organization(session, user.id, "123")


def test_user_organization_association(session):
    organization = get_factory("Organization", session).create(name="Test Organization")
    user = get_factory("User", session).create(fullname="John Doe")
    user.organizations.append(organization)
    assert user.organizations[0].name == "Test Organization"


def test_user_organization_association_reverse(session):
    organization = get_factory("Organization", session).create(name="Test Organization")
    user = get_factory("User", session).create(fullname="John Doe")
    organization.users.append(user)
    assert organization.users[0].fullname == "John Doe"


def test_agent_organization_association(session, user):
    organization = get_factory("Organization", session).create(name="Test Organization")
    agent = get_factory("Agent", session).create(user=user, name="Test Agent")
    agent.organization = organization
    assert agent.organization.name == "Test Organization"


def test_agent_organization_association_reverse(session, user):
    organization = get_factory("Organization", session).create(name="Test Organization")
    agent = get_factory("Agent", session).create(user=user, name="Test Agent")
    organization.agents.append(agent)
    assert organization.agents[0].name == "Test Agent"


def test_conversation_organization_association(session, user):
    organization = get_factory("Organization", session).create(name="Test Organization")
    conversation = get_factory("Conversation", session).create(
        title="Test Conversation", user_id=user.id
    )
    conversation.organization = organization
    assert conversation.organization.name == "Test Organization"


def test_conversation_organization_association_reverse(session, user):
    organization = get_factory("Organization", session).create(name="Test Organization")
    conversation = get_factory("Conversation", session).create(
        title="Test Conversation", user_id=user.id
    )
    organization.conversations.append(conversation)
    assert organization.conversations[0].title == "Test Conversation"
