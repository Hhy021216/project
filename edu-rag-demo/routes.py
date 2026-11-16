from pydantic import BaseModel, Field
from fastapi.templating import Jinja2Templates
from pathlib import Path
from fastapi import Request, APIRouter
from pipeline import QAPipeline


router = APIRouter()
templates = Jinja2Templates(Path(__file__).parent / 'templates')

@router.get('/')
def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": "EduRAG 智能问答",
            "message": "你好！我是智能问答助手，请输入你的问题。",
        },
    )


@router.get("/health")
def health():
    return {"status": "success"}

class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1)
    enable_rag: bool = True
    enable_web: bool = True
    
@router.post("/api/ask")
def ask(body: QueryRequest):
    return pipeline.query(
        body.question,
        enable_rag=body.enable_rag,
        enable_web=body.enable_web,
    )

# 定义请求参数
class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1)

# 定义接口函数
@router.post("/api/ask")
def ask(body: QueryRequest):
    question = body.question
    pipeline = QAPipeline()
    return pipeline.query(question)
