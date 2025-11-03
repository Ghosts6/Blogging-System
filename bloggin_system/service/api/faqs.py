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
    try:
        user = Token.objects.get(key=token).user
        new_faq = FAQ.objects.create(question=faq.question, answer=faq.answer, created_by=user)
        return FAQSerializer.from_orm(new_faq)
    except Token.DoesNotExist:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.get("/faqs/", response_model=List[FAQSerializer])
def list_faqs():
    faqs = FAQ.objects.all()
    return [FAQSerializer.from_orm(faq) for faq in faqs]

@router.get("/faqs/{faq_id}/", response_model=FAQSerializer)
def get_faq(faq_id: int):
    try:
        faq = FAQ.objects.get(id=faq_id)
        return FAQSerializer.from_orm(faq)
    except FAQ.DoesNotExist:
        raise HTTPException(status_code=404, detail="FAQ not found")

@router.put("/faqs/{faq_id}/", response_model=FAQSerializer)
def update_faq(faq_id: int, faq: FAQCreate, token: str = Depends(oauth2_scheme)):
    try:
        user = Token.objects.get(key=token).user
        existing_faq = FAQ.objects.get(id=faq_id, created_by=user)
        existing_faq.question = faq.question
        existing_faq.answer = faq.answer
        existing_faq.save()
        return FAQSerializer.from_orm(existing_faq)
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
