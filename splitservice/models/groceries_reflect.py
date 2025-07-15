from flask import current_app
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

Base = automap_base()
models = {}

def init_models():
    try:
        engine = current_app.engine
        Base.prepare(engine, reflect=True)
        models['groceries'] = Base.classes.get('groceries')
        if models['groceries']:
            logger.info("Successfully reflected 'groceries' table.")
        else:
            logger.warning("'groceries' table not found during reflection.")
    except Exception as e:
        logger.error(f"[splitService] Error reflecting groceries: {e}")

def get_session():
    try:
        engine = current_app.engine
        return Session(engine)
    except Exception as e:
        logger.error(f"Failed to create DB session: {e}")
        raise RuntimeError(f"Failed to create DB session: {e}")

__all__ = ['get_session', 'init_models', 'models']
