from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from tortoise.expressions import F

from core.auth import get_current_user
from dtos.schedule import *
from models.schedule import *
from models.user import User

router = APIRouter(prefix="/schedules")


@router.get("", response_model=List[ScheduleOut])
async def get_schedules(user: User = Depends(get_current_user)):
    schedules = (
        await Schedule.filter(user=user).prefetch_related("days", "exclusions").all()
    )
    return [ScheduleOut.from_orm(s) for s in schedules]


@router.post("", response_model=ScheduleOut)
async def create_schedule(data: ScheduleIn, user: User = Depends(get_current_user)):
    schedule = await Schedule.create(
        user=user,
        time=data.time,
        start_date=data.start_date,
        end_date=data.end_date,
    )

    for day in data.days:
        await ScheduleDay.create(schedule=schedule, day=day)

    await schedule.fetch_related("days", "exclusions")
    return ScheduleOut.from_orm(schedule)


@router.patch("/{schedule_id}", response_model=ScheduleOut)
async def patch_schedule(
    schedule_id: int,
    data: ScheduleIn,
    user: User = Depends(get_current_user),
):
    schedule = await Schedule.get_or_none(id=schedule_id, user=user).prefetch_related(
        "days", "exclusions"
    )

    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    if data.time is not None:
        schedule.time = data.time

    if data.start_date is not None:
        schedule.start_date = data.start_date

    if data.end_date is not None:
        schedule.end_date = data.end_date

    if data.days is not None:
        await ScheduleDay.filter(schedule=schedule).delete()
        for day in data.days:
            await ScheduleDay.create(schedule=schedule, day=day)

    await schedule.save()
    await schedule.fetch_related("days", "exclusions")
    return ScheduleOut.from_orm(schedule)


@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_schedule(
    schedule_id: int,
    user: User = Depends(get_current_user),
):
    schedule = await Schedule.get_or_none(id=schedule_id, user=user).prefetch_related(
        "days"
    )
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    yesterday = date.today() - timedelta(days=1)
    schedule_days = await ScheduleDay.filter(schedule=schedule).values_list(
        "day", flat=True
    )
    await Schedule.filter(id=schedule.id).update(end_date=yesterday)

    one_time_schedules = await Schedule.filter(
        user=user, start_date=F("end_date"), start_date__gte=date.today()
    ).prefetch_related("days")

    for s in one_time_schedules:
        s_days = await ScheduleDay.filter(schedule=s).values_list("day", flat=True)
        if any(day in schedule_days for day in s_days):
            await ScheduleDay.filter(schedule=s).delete()
            await s.exclusions.all().delete()
            await s.delete()


@router.post("/{schedule_id}/exclude", response_model=ScheduleOut)
async def createExclusion(
    schedule_id: int, data: ScheduleExclusionIn, user: User = Depends(get_current_user)
):
    schedule = await Schedule.get_or_none(id=schedule_id, user=user)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    await ScheduleExclusion.create(schedule=schedule, datetime=data.datetime)
    await schedule.fetch_related("days", "exclusions")
    return ScheduleOut.from_orm(schedule)
