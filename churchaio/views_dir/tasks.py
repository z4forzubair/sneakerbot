from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.template import loader

from churchaio.forms import TaskForm
from churchaio.models import Task
from churchaio.tasks import footlocker_bot_task
from sneakerbot_backend.celery import app


def render_tasks(request):
    user = request.user
    old_task = request.session.get('_old_task')
    request.session['_old_task'] = None
    form = TaskForm(old_task or None, user=request.user)
    tasks_list = Task.objects.filter(user=user).order_by('-created_at')
    count = tasks_list.count()
    forms_list = []
    for task in tasks_list:
        edit_form = TaskForm(user=user, instance=task)
        forms_list.append(edit_form)

    edit_tasks_list = zip(tasks_list, forms_list)
    context = {
        'segment': 'tasks',
        'edit_tasks_list': edit_tasks_list,
        'TASK_STATUS': Task.STATUS,
        'count': count,
        'form': form
    }
    html_template = loader.get_template('churchaio/tasks.html')
    response = HttpResponse(html_template.render(context, request))
    return response


def mature_task_status(task, proxy_list, profile):
    task_status = task.status
    task.status = Task.STATUS.MATURE if proxy_list is not None and profile is not None else Task.STATUS.IMMATURE
    if task.status != task_status:
        error = None
        msg = None
        try:
            task.save()
        except Exception as ex:
            error = ex
            msg = 'Could not mature task status'
        else:
            msg = 'Task status matured'


def perform_create_task(request):
    user = request.user
    form = TaskForm(request.POST, user=user)
    error = None
    if request.method == 'POST':
        if form.is_valid():
            form_data = form.cleaned_data
            try:
                task_count = form_data['task_count']
                for i in range(0, task_count):
                    task = Task(
                        store_name=form_data['store_name'],
                        shoe_size=form_data['shoe_size'] or -1,
                        sku_link=form_data['sku_link'],
                        proxy_list_id=form_data['proxy_list'].id if form_data['proxy_list'] is not None else None,
                        profile_id=form_data['profile'].id if form_data['profile'] is not None else None,
                        user_id=user.id
                    )
                    task.save()
                    mature_task_status(task, form_data['proxy_list'], form_data['profile'])
            except Exception as ex:
                error = ex
                msg = 'Task could not be created'
                messages.warning(request, msg)
            else:
                msg = 'Task created successfully'
                messages.success(request, msg)
        else:
            error = 'Invalid form'
            msg = 'Task could not be created'
            messages.warning(request, msg)
    if error is not None:
        request.session['_old_task'] = request.POST
    return redirect('tasks')


def perform_udpate_task(request, task_id):
    user = request.user
    if request.method == 'POST':
        try:
            task = Task.objects.filter(user_id=user.id).get(id=task_id)
        except Task.DoesNotExist:
            error = 'error'
            msg = 'The task does not exist'
            messages.warning(request, msg)
        else:
            form = TaskForm(request.POST, user=user)
            if form.is_valid():
                form_data = form.cleaned_data
                task.store_name = form_data['store_name']
                task.shoe_size = form_data['shoe_size'] or -1
                task.sku_link = form_data['sku_link']
                task.proxy_list_id = form_data['proxy_list'].id if form_data['proxy_list'] is not None else None
                task.profile_id = form_data['profile'].id if form_data['profile'] is not None else None
                try:
                    task.save()
                    mature_task_status(task, form_data['proxy_list'], form_data['profile'])
                except Exception as ex:
                    error = ex
                    msg = 'Task could not be updated'
                    messages.warning(request, msg)
                else:
                    msg = 'Task updated successfully'
                    messages.success(request, msg)
            else:
                error = 'Invalid form'
                msg = 'Task could not be updated'
                messages.warning(request, msg)

    return redirect('tasks')


def perform_delete_task(request, task_id):
    msg = None
    error = None
    if request.method == 'POST':
        try:
            task = Task.objects.filter(user_id=request.user).get(id=task_id)
        except Task.DoesNotExist:
            error = 'error'
            msg = 'The task does not exist'
            messages.warning(request, msg)
        else:
            try:
                task.delete()
            except Exception as ex:
                error = ex
                msg = 'Task could not be deleted'
                messages.warning(request, msg)
            else:
                msg = 'Task deleted!'
                messages.warning(request, msg)

    return redirect('tasks')


def perform_clear_tasks(request):
    error = None
    msg = None
    if request.method == 'POST':
        try:
            tasks = Task.objects.filter(user_id=request.user)
        except Task.DoesNotExist:
            msg = 'No tasks to delete'
            messages.warning(request, msg)
        else:
            try:
                tasks.delete()
            except Exception as ex:
                error = ex
                msg = 'Tasks could not be deleted'
                messages.warning(request, msg)
            else:
                msg = 'All tasks cleared!'
                messages.warning(request, msg)

    return redirect('tasks')


# running the tasks
# def failed_task_message(request):
#     msg = 'The task failed'
#     messages.warning(request, msg)


def start_task_operation(task):
    result = footlocker_bot_task.delay(task.id, task.user_id)
    task.celery_id = result.task_id
    task.status = Task.STATUS.RUNNING


def perform_task(request):
    task_id = request.POST.get('task_id')
    try:
        task = Task.objects.filter(user_id=request.user.id).get(id=task_id)
    except Task.DoesNotExist:
        error = 'error'
        msg = 'Unknown error'
        done = False
        # messages.warning(request, msg)
    else:
        if task.status == Task.STATUS.MATURE:

            # add the task to queue here

            try:
                start_task_operation(task)
                task.save()
            except Exception:
                msg = "Status update failed"
                done = False
            else:
                msg = "Task started"
                done = True

            # url = task.sku_link
            # bot = FootlockerBot(url=url, task=task)
            # if bot.returnStatus():
            #     if bot.addToCart():
            #         # add to cart successful
            #         if bot.checkout():
            #             msg = 'Successfully purchased'
            #             messages.success(request, msg)
            #         else:
            #             failed_task_message(request)
            #     else:
            #         failed_task_message(request)
            # else:
            #     failed_task_message(request)
        elif task.status == Task.STATUS.COMPLETED:
            msg = 'DONE'
            done = False
        else:
            msg = 'Inconceivable!'
            done = False

    data = {
        'msg': msg,
        'done': done
    }

    return JsonResponse(data)


def perform_all_tasks(request):
    try:
        tasks = Task.objects.filter(user_id=request.user.id).filter(status=Task.STATUS.MATURE)
    except Task.DoesNotExist:
        msg = 'No tasks found'
    else:
        if tasks.count() == 0:
            msg = "No tasks to run"
            messages.warning(request, msg)
        else:
            for task in tasks:
                start_task_operation(task)
            try:
                Task.objects.bulk_update(tasks, ['celery_id', 'status'])
            except Exception:
                msg = 'Unknown error'
                messages.warning(request, msg)
            else:
                msg = "All Tasks started successfully"
                messages.success(request, msg)
    return redirect('tasks')


def revoke_task_operation(task):
    app.control.revoke(task.celery_id, terminate=True)
    task.status = Task.STATUS.MATURE


def revoke_task(request):
    task_id = request.POST.get("task_id")
    try:
        task = Task.objects.filter(user_id=request.user.id).get(id=task_id)
    except Task.DoesNotExist:
        error = 'error'
        msg = "Unknown error"
        done = False
    else:
        if task.status == Task.STATUS.RUNNING:
            revoke_task_operation(task)
            try:
                task.save()
            except Exception:
                msg = "Status update failed"
                done = False
            else:
                msg = "Stopped"
                done = True
        else:
            msg = 'Inconceivable!'
            done = False

    data = {
        'msg': msg,
        'done': done
    }
    return JsonResponse(data)


def revoke_all_tasks(request):
    try:
        tasks = Task.objects.filter(user_id=request.user.id).filter(status=Task.STATUS.RUNNING)
    except Task.DoesNotExist:
        msg = 'No tasks found'
    else:
        if tasks.count() == 0:
            msg = 'No tasks to stop'
            messages.warning(request, msg)
        else:
            for task in tasks:
                revoke_task_operation(task)
            try:
                Task.objects.bulk_update(tasks, ['status'])
            except Exception:
                msg = 'Unknown error'
                messages.warning(request, msg)
            else:
                msg = "All Tasks stopped"
                messages.success(request, msg)
    return redirect('tasks')
