from datetime import date, timedelta
from typing import List

from fastapi import HTTPException
from tortoise.expressions import F

from dto.schedule import *
from model.schedule import *
from model.user import User


class ScheduleService:
    async def get_all(self, user: User) -> List[Schedule]:
        return await Schedule.filter(user=user).prefetch_related("days", "exclusions")

    async def create(self, data: ScheduleCreateIn, user: User) -> Schedule:
        schedule = await Schedule.create(
            user=user,
            time=data.time,
            start_datetime=data.start_datetime,
            end_datetime=data.end_datetime,
        )
        for day in data.days:
            await ScheduleDay.create(schedule=schedule, day=day)
        await schedule.fetch_related("days", "exclusions")
        return schedule

    async def patch(
        self, schedule_id: int, data: SchedulePatchIn, user: User
    ) -> Schedule:
        schedule = await Schedule.get_or_none(
            id=schedule_id, user=user
        ).prefetch_related("days", "exclusions")
        if not schedule:
            raise HTTPException(status_code=404, detail="Schedule not found")

        if data.time is not None:
            schedule.time = data.time
        if data.start_datetime is not None:
            schedule.start_datetime = data.start_datetime
        if data.end_datetime is not None:
            schedule.end_datetime = data.end_datetime
        if data.days is not None:
            await ScheduleDay.filter(schedule=schedule).delete()
            for day in data.days:
                await ScheduleDay.create(schedule=schedule, day=day)

        await schedule.save()
        await schedule.fetch_related("days", "exclusions")
        return schedule

    async def delete(self, schedule_id: int, user: User):
        schedule = await Schedule.get_or_none(
            id=schedule_id, user=user
        ).prefetch_related("days")
        if not schedule:
            raise HTTPException(status_code=404, detail="Schedule not found")

        yesterday = date.today() - timedelta(days=1)
        schedule_days = await ScheduleDay.filter(schedule=schedule).values_list(
            "day", flat=True
        )
        await Schedule.filter(id=schedule.id).update(end_datetime=yesterday)

        one_time_schedules = await Schedule.filter(
            user=user,
            start_datetime=F("end_datetime"),
            start_datetime__gte=date.today(),
        ).prefetch_related("days")

        for s in one_time_schedules:
            s_days = await ScheduleDay.filter(schedule=s).values_list("day", flat=True)
            if any(day in schedule_days for day in s_days):
                await ScheduleDay.filter(schedule=s).delete()
                await s.exclusions.all().delete()
                await s.delete()

    async def create_exclusion(
        self, schedule_id: int, data: ScheduleExclusionIn, user: User
    ) -> Schedule:
        schedule = await Schedule.get_or_none(id=schedule_id, user=user)
        if not schedule:
            raise HTTPException(status_code=404, detail="Schedule not found")

        await ScheduleExclusion.create(schedule=schedule, datetime=data.datetime)
        await schedule.fetch_related("days", "exclusions")
        return schedule
