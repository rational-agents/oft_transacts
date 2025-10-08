from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

# Ensure mappers are registered (import side effects)
# These imports are intentionally unused but required so SQLAlchemy sees all models
from . import users  # noqa: F401
from . import accounts  # noqa: F401
from . import transacts  # noqa: F401