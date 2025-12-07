from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
import uuid

Base = declarative_base()


class Book(Base):
    __tablename__="books"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, nullable=False)
    title = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    storage_path = Column(Text, nullable=False)
    vectorstore_path = Column(Text, nullable=False)
    status = Column(String, default="uploaded")
    uploaded_at = Column(DateTime, default=datetime.now)
    ingested_at = Column(DateTime, nullable=True)