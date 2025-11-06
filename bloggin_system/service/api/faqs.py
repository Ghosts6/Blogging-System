from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from service.schemas import FAQSerializer
from service.models import FAQ
from rest_framework.authtoken.models import Token
from fastapi.security import OAuth2PasswordBearer
from django.contrib.auth import get_user_model

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
User = get_user_model()

class FAQCreate(BaseModel):
    question: str
    answer: str

@router.post("/faqs/", response_model=FAQSerializer)
def create_faq(faq: FAQCreate, token: str = Depends(oauth2_scheme)):
    from service.schemas import UserSerializer
    try:
        user = Token.objects.get(key=token).user
        new_faq = FAQ.objects.create(question=faq.question, answer=faq.answer, created_by=user)
        return FAQSerializer(
            id=new_faq.id,
            question=new_faq.question,
            answer=new_faq.answer,
            created_by=UserSerializer(
                id=user.id,
                username=user.username,
                email=user.email
            )
        )
    except Token.DoesNotExist:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.get("/faqs/", response_model=List[FAQSerializer])
def list_faqs():
    from service.schemas import UserSerializer
    faqs = FAQ.objects.select_related('created_by').all()
    result = []
    for faq in faqs:
        result.append(FAQSerializer(
            id=faq.id,
            question=faq.question,
            answer=faq.answer,
            created_by=UserSerializer(
                id=faq.created_by.id,
                username=faq.created_by.username,
                email=faq.created_by.email
            )
        ))
    return result

@router.get("/faqs/{faq_id}/", response_model=FAQSerializer)
def get_faq(faq_id: int):
    from service.schemas import UserSerializer
    try:
        faq = FAQ.objects.select_related('created_by').get(id=faq_id)
        return FAQSerializer(
            id=faq.id,
            question=faq.question,
            answer=faq.answer,
            created_by=UserSerializer(
                id=faq.created_by.id,
                username=faq.created_by.username,
                email=faq.created_by.email
            )
        )
    except FAQ.DoesNotExist:
        raise HTTPException(status_code=404, detail="FAQ not found")

@router.put("/faqs/{faq_id}/", response_model=FAQSerializer)
def update_faq(faq_id: int, faq: FAQCreate, token: str = Depends(oauth2_scheme)):
    from service.schemas import UserSerializer
    try:
        user = Token.objects.get(key=token).user
        existing_faq = FAQ.objects.select_related('created_by').get(id=faq_id, created_by=user)
        existing_faq.question = faq.question
        existing_faq.answer = faq.answer
        existing_faq.save()
        return FAQSerializer(
            id=existing_faq.id,
            question=existing_faq.question,
            answer=existing_faq.answer,
            created_by=UserSerializer(
                id=user.id,
                username=user.username,
                email=user.email
            )
        )
    except Token.DoesNotExist:
        raise HTTPException(status_code=401, detail="Invalid token")
    except FAQ.DoesNotExist:
        raise HTTPException(status_code=404, detail="FAQ not found")

@router.delete("/faqs/{faq_id}/")
def delete_faq(faq_id: int, token: str = Depends(oauth2_scheme)):
    try:
        user = Token.objects.get(key=token).user
        faq = FAQ.objects.get(id=faq_id, created_by=user)
        faq.delete()
        return {"message": "FAQ deleted successfully"}
    except Token.DoesNotExist:
        raise HTTPException(status_code=401, detail="Invalid token")
    except FAQ.DoesNotExist:
        raise HTTPException(status_code=404, detail="FAQ not found")
