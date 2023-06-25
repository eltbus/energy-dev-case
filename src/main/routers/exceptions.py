from contextlib import contextmanager

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError, NoResultFound
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

@contextmanager
def handle_upsert():
    """
    A context manager for handling exceptions during the upsert operation.

    Raises:
        HTTPException: For various error scenarios:
            - HTTP_400_BAD_REQUEST for an invalid row format.
            - HTTP_409_CONFLICT for integrity errors during upsert.
            - HTTP_500_INTERNAL_SERVER_ERROR for other exceptions.
    """
    try:
        yield
    except KeyError:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Invalid row format. Upload aborted.")
    except NoResultFound as e:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=repr(e))
    except IntegrityError as e:
        raise HTTPException(status_code=HTTP_409_CONFLICT, detail=repr(e))
    except Exception:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="There was an error uploading the file")
