from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.database_models import Organization


def seed_default_organization(op):
    """
    Seed default organization.
    """
    # Previously we would seed the default deployments and models here. We've changed this
    # behaviour during a refactor of the deployments module so that deployments and models
    # are inserted when they're first used. This solves an issue where seed data would
    # sometimes be inserted with invalid config data.

    _ = Session(op.get_bind())

    # Seed default organization
    sql_command = text(
        """
        INSERT INTO organizations (
            id, name, created_at, updated_at
        )
        VALUES (
            :id, :name, now(), now()
        )
        ON CONFLICT (id) DO NOTHING;
    """
    ).bindparams(
        id="default",
        name="Default Organization",
    )
    op.execute(sql_command)


def delete_default_organization(op):
    """
    Delete default organization.
    """
    session = Session(op.get_bind())
    session.query(Organization).filter_by(id="default").delete()
    session.commit()
