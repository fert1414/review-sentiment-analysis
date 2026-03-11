from pydantic import BaseModel, HttpUrl


class ImportForm(BaseModel):
    imdb_url: HttpUrl