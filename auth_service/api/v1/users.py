from uuid import UUID

from fastapi import APIRouter, HTTPException
from models import Role, User
from schemas import UserInDB
from starlette import status

router = APIRouter()


@router.get('/', response_model=list[UserInDB])
async def get_users() -> list[User]:
    users = await User.get_all()
    return users


@router.get('/{id}', response_model=UserInDB)
async def get_user(id: UUID) -> User:
    user = await User.get_by_id(id_=id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='User doesn\'t exists'
        )

    return user


@router.delete('/{id}', response_model=UserInDB)
async def delete_user(id: UUID) -> User:
    user = await User.get_by_id(id_=id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='User doesn\'t exists'
        )

    return await user.delete()


@router.post('/{id}/set_role', response_model=UserInDB)
async def set_role(id: UUID, role_id: UUID) -> User:
    user = await User.get_by_id(id_=id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='User doesn\'t exists'
        )

    role = await Role.get_by_id(id_=role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Role doesn\'t exists'
        )

    user.role_id = role_id
    await user.save()

    return user


@router.post('/{id}/remove_role', response_model=UserInDB)
async def remove_role(id: UUID) -> User:
    user = await User.get_by_id(id_=id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='User doesn\'t exists'
        )

    user.role_id = None
    await user.save()

    return user
