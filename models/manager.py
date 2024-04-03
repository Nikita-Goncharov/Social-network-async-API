from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession


# TODO: chaining
class Manager:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, model, data):
        instance = model(**data)
        self.session.add(instance)
        await self.session.commit()
        return instance

    async def update(self, model, data):
        instance_id = int(data.pop("id"))
        await self.session.execute(update(model).where(model.id == instance_id).values(data))
        await self.session.commit()

    async def delete(self, model, instance_id):
        await self.session.execute(delete(model).where(id=instance_id))
        await self.session.commit()

    async def filter(self, model, **kwargs):
        cursor = await self.session.execute(select(model).where(**kwargs))
        return cursor.all()

    async def get(self, model, instance_id):
        return await self.session.get(model, instance_id)

    async def pagination_getting(self, model, page=1, count=10):
        record_start_from = (page - 1) * count

        cursor = await self.session.execute(select(model).limit(count).offset(record_start_from))

        count_records = select(func.count("*").label("total")).select_from(model)
        total_count_cursor = await self.session.execute(count_records)
        instances = cursor.all()
        total_count = total_count_cursor.mappings().first()
        return instances, dict(total_count)["total"]

    async def all(self, model):
        cursor = await self.session.execute(select(model))
        return cursor.all()

    async def count(self, model):
        cursor = await self.session.execute(select(func.count("*").label("total")).select_from(model))
        return cursor.first()._asdict()["total"]