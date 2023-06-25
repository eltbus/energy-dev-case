from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError, NoResultFound
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
import pytest

from main.routers.exceptions import handle_upsert


def test_handle_upsert_maps_KeyError_to_HTTP_400_BAD_REQUEST():
    with pytest.raises(HTTPException) as e:
        with handle_upsert():
            raise KeyError
    assert e.value.status_code == HTTP_400_BAD_REQUEST


def test_handle_upsert_maps_NoResultFound_to_HTTP_404_NOT_FOUND():
    with pytest.raises(HTTPException) as e:
        with handle_upsert():
            raise NoResultFound
    assert e.value.status_code == HTTP_404_NOT_FOUND


def test_handle_upsert_maps_IntegrityError_to_HTTP_409_CONFLICT():
    with pytest.raises(HTTPException) as e:
        with handle_upsert():
            # NOTE: IntegrityError requires params
            raise IntegrityError(statement=None, params=None, orig=Exception())
    assert e.value.status_code == HTTP_409_CONFLICT


def test_handle_upsert_maps_generic_Exception_to_HTTP_500_INTERNAL_SERVER_ERROR():
    with pytest.raises(HTTPException) as e:
        with handle_upsert():
            raise Exception
    assert e.value.status_code == HTTP_500_INTERNAL_SERVER_ERROR
