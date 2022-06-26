from churchaio.models import Task


class MyException(Exception):
    pass


def task_failed(task_id, status):
    print(status.label)
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        msg = "Task not found"
    else:
        task.status = status
        try:
            task.save()
        except Exception:
            msg = "Task not found"
    finally:
        raise MyException


def task_completed(task_id):
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        msg = "Task not found"
    else:
        task.status = Task.STATUS.COMPLETED
        try:
            task.save()
        except Exception:
            msg = "Task not found"
