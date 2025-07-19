from datetime import date, timedelta, time
from typing import List

from fastapi import HTTPException

from dto.schedule import *
from model.schedule import *
from model.user import User


class ScheduleService:
    async def get_all(self, user: User) -> List[Schedule]:
        return await Schedule.filter(user=user).prefetch_related(
            "days", "exclusions", "time_modifications"
        )

    async def create(self, data: ScheduleCreateIn, user: User) -> Schedule:
        schedule = await Schedule.create(
            user=user,
            time=data.time,
            start_datetime=data.start_datetime,
            end_datetime=data.end_datetime,
        )

        await ScheduleDay.bulk_create(
            [ScheduleDay(schedule=schedule, day=day) for day in data.days]
        )

        await schedule.fetch_related("days", "exclusions", "time_modifications")
        return schedule

    async def delete(self, id: int, user: User):
        schedule = await Schedule.get_or_none(id=id, user=user).prefetch_related(
            "days", "exclusions", "time_modifications"
        )
        if not schedule:
            raise HTTPException(status_code=404, detail="Schedule not found")

        yesterday = date.today() - timedelta(days=1)
        await Schedule.filter(id=schedule.id).update(end_datetime=yesterday)

    async def replace(
        self, schedule_id: int, data: ScheduleReplaceIn, user: User
    ) -> Schedule:
        schedule = await Schedule.get_or_none(
            id=schedule_id, user=user
        ).prefetch_related("days", "exclusions", "time_modifications")
        if not schedule:
            raise HTTPException(status_code=404, detail="Schedule not found")

        schedule.end_datetime = date.today() - timedelta(days=1)
        await schedule.save()

        new_schedule = await Schedule.create(
            user=user,
            time=data.time,
            start_datetime=datetime.now(),
        )

        days = data.days
        await ScheduleDay.bulk_create(
            [ScheduleDay(schedule=new_schedule, day=day) for day in days]
        )

        today = datetime.combine(date.today(), time.min)
        mods = await ScheduleTimeModification.filter(
            schedule=schedule,
            datetime__gte=today,
        ).all()
        await ScheduleTimeModification.bulk_create(
            [
                ScheduleTimeModification(schedule=new_schedule, datetime=mod.datetime)
                for mod in mods
            ]
        )

        await new_schedule.fetch_related("days", "exclusions", "time_modifications")
        return new_schedule

    async def create_time_modification(
        self, id: int, data: ScheduleTimeModificationIn, user: User
    ) -> Schedule:
        schedule = await Schedule.get_or_none(id=id, user=user)
        if not schedule:
            raise HTTPException(status_code=404, detail="Schedule not found")

        day_start = datetime.combine(data.datetime, time.min)
        day_end = day_start + timedelta(days=1)

        await ScheduleTimeModification.update_or_create(
            defaults={"datetime": data.datetime},
            schedule=schedule,
            datetime__gte=day_start,
            datetime__lt=day_end,
        )

        await schedule.fetch_related("days", "exclusions", "time_modifications")
        return schedule

    async def create_exclusion(
        self, id: int, data: ScheduleExclusionIn, user: User
    ) -> Schedule:
        schedule = await Schedule.get_or_none(id=id, user=user)
        if not schedule:
            raise HTTPException(status_code=404, detail="Schedule not found")

        await ScheduleExclusion.create(schedule=schedule, datetime=data.datetime)
        await schedule.fetch_related("days", "exclusions", "time_modifications")
        return schedule
