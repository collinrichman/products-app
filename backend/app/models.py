from pydantic import BaseModel, field_validator


class ProductCreate(BaseModel):
    name: str
    popularity: int = 0

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, name: str) -> str:
        name = name.strip()
        if not name:
            raise ValueError("name must not be blank")
        return name


class Product(BaseModel):
    id: int
    name: str
    popularity: int
