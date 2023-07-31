from pydantic import BaseModel

class BorrowUmbrellaSchema(BaseModel):
    user_id: int
    umbrella_id: int

class ReturnUmbrellaSchema(BaseModel):
    umbrella_id: int
