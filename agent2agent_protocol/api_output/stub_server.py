from datetime import datetime, timezone
import uuid
from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel, Field
import uvicorn

app = FastAPI(title="todo_list_api", version="1.0.0")

todos_db = {}


class CreateTodoRequest(BaseModel):
    title: str
    description: str | None = None


class UpdateTodoRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    completed: bool | None = None


@app.post("/api/v1/todos", status_code=status.HTTP_201_CREATED)
def create_todo(payload: CreateTodoRequest):
    todo_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    todo = {
        "id": todo_id,
        "title": payload.title,
        "description": payload.description,
        "completed": False,
        "created_at": now,
    }
    todos_db[todo_id] = todo
    return todo


@app.get("/api/v1/todos")
def list_todos():
    items = list(todos_db.values())
    return {"data": items, "count": len(items)}


@app.get("/api/v1/todos/{id}")
def get_todo(id: str):
    if id not in todos_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Todo not found"},
        )
    return todos_db[id]


@app.put("/api/v1/todos/{id}")
def update_todo(id: str, payload: UpdateTodoRequest):
    if id not in todos_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Todo not found"},
        )

    existing = todos_db[id]
    update_data = payload.model_dump(exclude_unset=True)

    if "title" in update_data:
        existing["title"] = update_data["title"]
    if "description" in update_data:
        existing["description"] = update_data["description"]
    if "completed" in update_data:
        existing["completed"] = update_data["completed"]

    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    updated_todo = {
        "id": existing["id"],
        "title": existing["title"],
        "description": existing["description"],
        "completed": existing["completed"],
        "updated_at": now,
    }
    todos_db[id].update(updated_todo)
    return updated_todo


@app.delete("/api/v1/todos/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(id: str):
    if id not in todos_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Todo not found"},
        )
    del todos_db[id]
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.exception_handler(422)
async def validation_exception_handler(request, exc):
    from fastapi.responses import JSONResponse

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": "Invalid request payload"},
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)