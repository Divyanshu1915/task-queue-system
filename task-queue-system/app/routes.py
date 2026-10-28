from flask import Blueprint , request
from app import db
from app.models import Task

main = Blueprint("main" , __name__)

@main.route("/")
def home():
    return {"message" : "Task Queue System is running"}


            
@main.route("/tasks" , methods=["POST"])
def create_task():
    data= request.get_json()
    
    
    
    if not data:
        return {"error" : "request body is required"} ,400
    
    name = data.get("name")
    priority=data.get("priority")
    
    if not isinstance(name , str) or not name.strip():
        return {"error" : "TAsk must not be empty "} ,400
    
    if "name" not in data:
        return {"error" : "task name is required "}, 400
    
    if "priority" not in data:
        return {"error" : "task priority is required"}, 400
    if priority not in ["low" , "high" , "high"]:
        return {"error" : "Invalid priority " } , 400
    
    task = Task(name=name , priority = priority)
    
    db.session.add(task)
    db.session.commit()
    
    return{
        "message" : "Task created Successfully",
        "Task" : {
            "id" : task.id,
            "name" : task.name,
            "priority" : task.priority 
        }
    } , 201
    

    

@main.route("/tasks", methods=["GET"])
def get_tasks():
    priority = request.args.get("priority")
    status = request.args.get("status")

    query = Task.query

    if priority:
        if priority not in ["low", "medium", "high"]:
            return {"error": "Invalid priority"}, 400

        query = query.filter_by(priority=priority)

    if status:
        if status not in ["pending", "running", "completed", "failed"]:
            return {"error": "Invalid task status"}, 400

        query = query.filter_by(status=status)

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 5, type=int)

    if page < 1 or per_page < 1 or per_page > 100:
        return {"error": "Invalid pagination values"}, 400
    
    sort_by = request.args.get("sort_by", "id")

    if sort_by == "priority":
        query = query.order_by(
            db.case(
                (Task.priority == "high", 1),
                (Task.priority == "medium", 2),
                (Task.priority == "low", 3),
                else_=4
            )
        )
    elif sort_by == "id":
        query = query.order_by(Task.id.asc())
    else:
        return {"error": "Invalid sort field"}, 400
    pagination = query.paginate(
    page=page,
    per_page=per_page,
    error_out=False
)

    tasks = pagination.items

    return {
    "tasks": [
        {
            "id": task.id,
            "name": task.name,
            "priority": task.priority,
            "status": task.status
        }
        for task in tasks
    ],
    "pagination": {
        "page": pagination.page,
        "per_page": pagination.per_page,
        "total_tasks": pagination.total,
        "total_pages": pagination.pages
    }
    }, 200


@main.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    task = db.session.get(Task, task_id)

    if task is None:
        return {"error": "Task not found"}, 404

    return {
        "id": task.id,
        "name": task.name,
        "priority": task.priority,
        "status": task.status,
        "retry_count": task.retry_count,
        "max_retries": task.max_retries
    }, 200

    
    
# Now to add a delete route 
# Add a delete API

@main.route("/tasks/<int:task_id>" , methods = ["DELETE"])
def delete_task(task_id):
    task = db.session.get(Task , task_id)
    
    if task is None:
        return {"error" : "Task not found"} , 404 
    
    db.session.delete(task)
    db.session.commit()
    
    return {"message" : " Task deleted successfully" } , 200


@main.route("/tasks/<int:task_id>/status", methods=["PATCH"])
def update_task_status(task_id):
    data = request.get_json()

    if not data or "status" not in data:
        return {"error": "Task status is required"}, 400

    status = data["status"]

    if status not in ["pending", "running", "completed", "failed"]:
        return {"error": "Invalid task status"}, 400

    task = db.session.get(Task, task_id)

    if task is None:
        return {"error": "Task not found"}, 404

    task.status = status
    db.session.commit()

    return {
        "message": "Task status updated successfully",
        "task": {
            "id": task.id,
            "name": task.name,
            "priority": task.priority,
            "status": task.status
        }
    }, 200
    

@main.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    task = db.session.get(Task, task_id)

    if task is None:
        return {"error": "Task not found"}, 404

    data = request.get_json()

    if not data:
        return {"error": "Request body is required"}, 400

    name = data.get("name")
    priority = data.get("priority")

    if not isinstance(name, str) or not name.strip():
        return {"error": "Task name must not be empty"}, 400

    if priority not in ["low", "medium", "high"]:
        return {"error": "Invalid priority"}, 400

    task.name = name.strip()
    task.priority = priority

    db.session.commit()

    return {
        "message": "Task updated successfully",
        "task": {
            "id": task.id,
            "name": task.name,
            "priority": task.priority,
            "status": task.status
        }
    }, 200

