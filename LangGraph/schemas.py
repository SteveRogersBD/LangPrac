from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Literal


class Video(BaseModel):
    """
    input object: what video we are analyzing.
    """
    url: Optional[str] = Field(None, description="youtube video url")
    title: Optional[str] = Field(None, description="optional: title if you already know it")
    target_age: Optional[int] = Field(None, description="optional: used to simplify wording")
    max_questions: int = Field(10, ge=1, le=50, description="how many questions to generate")
    difficulty: Literal["easy", "medium"] = Field("easy", description="difficulty level for the quiz")


class Question(BaseModel):
    """
    output object: one quiz question extracted/derived from the video.
    """
    prompt: str = Field(..., min_length=3, description="the question text")
    choices: List[str] = Field(..., min_items=2, max_items=6, description="answer options")
    answer_index: int = Field(..., ge=0, description="index into choices list")
    explanation: Optional[str] = Field(None, description="optional: short reason why answer is correct")
    timestamp_sec: Optional[int] = Field(None, ge=0, description="optional: where this appeared in the video")


class Quiz(BaseModel):
    """
    final response: quiz for a given video.
    """
    video: Video
    questions: List[Question] = Field(..., min_items=1)
