from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class UserRole(enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    STAFF = "staff"
    VIEWER = "viewer"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    role = Column(Enum(UserRole), default=UserRole.STAFF, nullable=False)
    department = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has specific permission based on role"""
        role_permissions = {
            UserRole.ADMIN: [
                "create_po", "edit_po", "delete_po", "approve_po", "cancel_po", 
                "receive_po", "view_all_po", "manage_users", "manage_suppliers",
                "manage_products", "manage_inventory", "view_reports"
            ],
            UserRole.MANAGER: [
                "create_po", "edit_po", "approve_po", "cancel_po", 
                "receive_po", "view_all_po", "manage_suppliers",
                "manage_products", "manage_inventory", "view_reports"
            ],
            UserRole.STAFF: [
                "create_po", "edit_po", "receive_po", "view_own_po"
            ],
            UserRole.VIEWER: [
                "view_own_po"
            ]
        }
        return permission in role_permissions.get(self.role, [])
    
    def can_approve_po(self) -> bool:
        """Check if user can approve purchase orders"""
        return self.role in [UserRole.ADMIN, UserRole.MANAGER]
    
    def can_cancel_po(self) -> bool:
        """Check if user can cancel purchase orders"""
        return self.role in [UserRole.ADMIN, UserRole.MANAGER]
    
    def can_receive_po(self) -> bool:
        """Check if user can receive purchase orders"""
        return self.role in [UserRole.ADMIN, UserRole.MANAGER, UserRole.STAFF]
    
    def can_edit_po(self) -> bool:
        """Check if user can edit purchase orders"""
        return self.role in [UserRole.ADMIN, UserRole.MANAGER, UserRole.STAFF] 