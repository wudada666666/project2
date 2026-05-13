from pydantic import BaseModel


class ProgressMark(BaseModel):
    word_id: int
    status: int  # 0=未标记 1=已掌握 2=模糊 3=不认识


class FavoriteMark(BaseModel):
    word_id: int
    action: str = "add"  # add / remove
