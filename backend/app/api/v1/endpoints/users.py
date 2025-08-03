from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_active_user, verify_password
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate, User as UserSchema, UserWithPermissions
from app.core.security import get_password_hash

router = APIRouter()

def convert_user_to_user_with_permissions(user: User) -> UserWithPermissions:
    """Convert User model to UserWithPermissions schema with calculated permissions"""
    return UserWithPermissions(
        id=user.id,
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        role=user.role,
        department=user.department,
        phone=user.phone,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        created_at=user.created_at,
        updated_at=user.updated_at,
        can_approve_po=user.can_approve_po(),
        can_cancel_po=user.can_cancel_po(),
        can_receive_po=user.can_receive_po(),
        can_edit_po=user.can_edit_po(),
        can_manage_users=user.has_permission("manage_users"),
        can_view_reports=user.has_permission("view_reports")
    )

@router.get("/", response_model=List[UserWithPermissions])
def read_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve users (Admin/Manager only).
    """
    if not current_user.has_permission("manage_users"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    users = db.query(User).offset(skip).limit(limit).all()
    
    # Convert to UserWithPermissions with calculated permissions
    users_with_permissions = [convert_user_to_user_with_permissions(user) for user in users]
    return users_with_permissions

@router.post("/", response_model=UserWithPermissions)
def create_user(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    user_in: UserCreate,
) -> Any:
    """
    Create new user (Admin/Manager only).
    """
    if not current_user.has_permission("manage_users"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == user_in.email) | (User.username == user_in.username)
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or username already exists"
        )
    
    # Create new user
    user_data = user_in.dict()
    user_data["hashed_password"] = get_password_hash(user_in.password)
    del user_data["password"]
    
    user = User(**user_data)
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Return with permissions
    return convert_user_to_user_with_permissions(user)

@router.get("/me", response_model=UserWithPermissions)
def read_current_user(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get current user with permissions.
    """
    return convert_user_to_user_with_permissions(current_user)

@router.get("/{user_id}", response_model=UserWithPermissions)
def read_user(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    user_id: int,
) -> Any:
    """
    Get user by ID (Admin/Manager only, or own profile).
    """
    if current_user.id != user_id and not current_user.has_permission("manage_users"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return convert_user_to_user_with_permissions(user)

@router.put("/{user_id}", response_model=UserWithPermissions)
def update_user(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    user_id: int,
    user_in: UserUpdate,
) -> Any:
    """
    Update user (Admin/Manager only, or own profile).
    """
    if current_user.id != user_id and not current_user.has_permission("manage_users"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    update_data = user_in.dict(exclude_unset=True)
    
    # Handle password update
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return convert_user_to_user_with_permissions(user)

@router.delete("/{user_id}")
def delete_user(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    user_id: int,
) -> Any:
    """
    Delete user (Admin only).
    """
    if not current_user.has_permission("manage_users"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}

@router.get("/roles/available", response_model=List[str])
def get_available_roles(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get available user roles (Admin/Manager only).
    """
    if not current_user.has_permission("manage_users"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return [role.value for role in UserRole]

@router.post("/change-password")
def change_password(
    password_data: dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Change user password"""
    if not verify_password(password_data["current_password"], current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    current_user.hashed_password = get_password_hash(password_data["new_password"])
    db.commit()
    
    return {"message": "Password changed successfully"} 