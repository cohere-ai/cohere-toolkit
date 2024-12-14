from sqlalchemy.orm import Session

from backend.database_models import Deployment, Model, Organization


def deployments_models_seed(op):
    """
    Seed default deployments, models, organization, user and agent.
    """
    # Previously we would seed the default deployments and models here. We've changed this
    # behaviour during a refactor of the deployments module so that deployments and models
    # are inserted when they're first used. This solves an issue where seed data would
    # sometimes be inserted with invalid config data.
    pass


def delete_default_models(op):
    """
    Delete deployments and models.
    """
    session = Session(op.get_bind())
    session.query(Deployment).delete()
    session.query(Model).delete()
    session.query(Organization).filter_by(id="default").delete()
    session.commit()
