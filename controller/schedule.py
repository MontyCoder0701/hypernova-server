from fastapi import APIRouter, Depends, status
from typing import List

from core.auth import get_current_user
from dto.schedule import *
from model.user import User
from service.schedule import ScheduleService

router = APIRouter(prefix="/schedules")


@router.get("", response_model=List[ScheduleOut])
async def get_schedules(
    user: User = Depends(get_current_user), service: ScheduleService = Depends()
):
    schedules = await service.get_all(user)
    return [ScheduleOut.from_orm(s) for s in schedules]


@router.post("", response_model=ScheduleOut)
async def create_schedule(
    data: ScheduleCreateIn,
    user: User = Depends(get_current_user),
    service: ScheduleService = Depends(),
):
    schedule = await service.create(data, user)
    return ScheduleOut.from_orm(schedule)


@router.patch("/{schedule_id}", response_model=ScheduleOut)
async def patch_schedule(
    schedule_id: int,
    data: SchedulePatchIn,
    user: User = Depends(get_current_user),
    service: ScheduleService = Depends(),
):
    schedule = await service.patch(schedule_id, data, user)
    return ScheduleOut.from_orm(schedule)


@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_schedule(
    schedule_id: int,
    user: User = Depends(get_current_user),
    service: ScheduleService = Depends(),
):
    await service.delete(schedule_id, user)


@router.post("/{schedule_id}/exclude", response_model=ScheduleOut)
async def create_exclusion(
    schedule_id: int,
    data: ScheduleExclusionIn,
    user: User = Depends(get_current_user),
    service: ScheduleService = Depends(),
):
    schedule = await service.create_exclusion(schedule_id, data, user)
    return ScheduleOut.from_orm(schedule)
