from uuid import UUID, uuid4
import pathlib

from fastapi import Depends, UploadFile
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from decouple import config

from app.db.db import db_session
from app.db.models import Image

IMAGE_PATH = config("IMAGE_PATH")
async def upload_image(image: UploadFile, film_id: UUID, is_cover: bool | None, session: AsyncSession = Depends(db_session)):
    random_name = uuid4()
    extension = "".join(pathlib.Path(image.filename).suffixes)

    path = pathlib.Path(f"{IMAGE_PATH}/{str(random_name)}{extension}")
    print(path)
    try:
        with path.open("wb") as buffer:
            buffer.write(image.file.read())
    except:
        raise TypeError()
    finally:
        image.file.close()
        
    new_image = Image(
        image_id=random_name,
        film_id=film_id,
        image_extension=image.content_type,
        is_cover=is_cover,
    )

    return new_image

    
    
async def delete_image(image_id: UUID, session: AsyncSession = Depends(db_session)):
    statement = select(Image).where(Image.image_id == image_id)
    result = await session.exec(statement)
    image = result.first()

    if image == None:
        raise FileNotFoundError()
    
    path = pathlib.Path(f"{IMAGE_PATH}/{str(image.image_id)}{image.image_extension}")
    
    await session.delete(image)
    try:
        path.unlink()
    except:
        await session.rollback()
        raise FileNotFoundError()
    
    await session.commit()
    

        