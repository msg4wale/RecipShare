from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def set_password(self, password: str):
        """Hash password using PBKDF2-SHA256"""
        from app.auth import pwd_context
        self.password_hash = pwd_context.hash(password)

    def verify_password(self, password: str) -> bool:
        """Verify password against hash"""
        from app.auth import pwd_context
        return pwd_context.verify(password, self.password_hash)

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"
