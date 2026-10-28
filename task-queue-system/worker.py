
import time

from app import create_app, db
from app.models import Task

app = create_app()


def run_worker():
    print("Task worker started...")

    while True:
        with app.app_context():
            task = (
                Task.query
                .filter_by(status="pending")
                .order_by(
                    db.case(
                        (Task.priority == "high", 1),
                        (Task.priority == "medium", 2),
                        (Task.priority == "low", 3),
                        else_=4
                    ),
                    Task.id.asc()
                )
                .first()
            )

            if task:
                task.status = "running"
                db.session.commit()

                print(f"Running task {task.id}: {task.name}")
                print(f"DEBUG task name: {task.name!r}")
                

               
                try:
                    # Temporary simulated task execution
                    time.sleep(3)

                    if task.name == "Retry test":
                        raise Exception("Simulated task failure")

                    task.status = "completed"
                    db.session.commit()

                    print(f"Task {task.id} completed!")

                except Exception as error:
                    db.session.rollback()

                    task = db.session.get(Task, task.id)

                    if task.retry_count < task.max_retries:
                        task.retry_count += 1
                        task.status = "pending"
                        db.session.commit()

                        print(
                            f"Task {task.id} failed. "
                            f"Retry {task.retry_count}/{task.max_retries}: {error}"
                        )
                    else:
                        task.status = "failed"
                        db.session.commit()

                        print(
                            f"Task {task.id} permanently failed "
                            f"after {task.retry_count} retries."
                        )


        time.sleep(1)


if __name__ == "__main__":
    run_worker()
