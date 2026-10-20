import os
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import select, String
import boto3

DB_URL = os.getenv("DB_URL", "postgresql+asyncpg://catalog_user:catalog_password@localhost:5432/catalog_db")
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadminpassword")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "catalog-images")

engine = create_async_engine(DB_URL)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

class Product(Base):
    __tablename__ = "products"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String, nullable=False)
    image_url: Mapped[str] = mapped_column(String, nullable=False)

def get_s3_client():
    return boto3.client(
        's3',
        endpoint_url=f"http://{MINIO_ENDPOINT}",
        aws_access_key_id=MINIO_ACCESS_KEY,
        aws_secret_access_key=MINIO_SECRET_KEY,
    )

def ensure_bucket_exists():
    s3 = get_s3_client()
    try:
        s3.head_bucket(Bucket=MINIO_BUCKET)
    except Exception:
        s3.create_bucket(Bucket=MINIO_BUCKET)

@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_bucket_exists()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/products")
async def create_product(title: str = Form(...), file: UploadFile = File(...)):
    s3 = get_s3_client()
    file_ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    filename = f"{uuid.uuid4()}.{file_ext}"
    
    contents = await file.read()
    s3.put_object(
        Bucket=MINIO_BUCKET,
        Key=filename,
        Body=contents,
        ContentType=file.content_type or "image/jpeg"
    )
    
    image_url = f"http://{MINIO_ENDPOINT}/{MINIO_BUCKET}/{filename}"
    
    async with AsyncSessionLocal() as session:
        product = Product(title=title, image_url=image_url)
        session.add(product)
        await session.commit()
        await session.refresh(product)
        return {"id": product.id, "title": product.title, "image_url": product.image_url}

@app.get("/products")
async def get_products():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Product))
        products = result.scalars().all()
        return [{"id": p.id, "title": p.title, "image_url": p.image_url} for p in products]
