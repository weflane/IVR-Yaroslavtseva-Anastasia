from fastapi import APIRouter, Depends, HTTPException
from app import models, schemas
from app.auth_utils import require_admin

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("", response_model=list[schemas.TagOut])
def list_tags():
    """Get all tags (for tag cloud)"""
    tags = models.Tag.objects().order_by('category', 'name')
    return list(tags)


@router.get("/category/{category}", response_model=list[schemas.TagOut])
def get_tags_by_category(category: str):
    """Get tags by category"""
    tags = models.Tag.objects(category=category).order_by('name')
    return list(tags)


@router.post("", response_model=schemas.TagOut, status_code=201)
def create_tag(
    body: schemas.TagCreate,
    _=Depends(require_admin)
):
    """Create new tag (admin only)"""
    existing = models.Tag.objects(name=body.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Тег с таким названием уже существует")

    tag = models.Tag(
        name=body.name,
        category=body.category
    )
    tag.save()
    return tag


@router.delete("/{tag_id}", status_code=204)
def delete_tag(
    tag_id: str,
    _=Depends(require_admin)
):
    """Delete tag (admin only)"""
    tag = models.Tag.objects(id=tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Тег не найден")

    tag.delete()
    return None
