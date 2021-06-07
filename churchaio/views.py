from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django import template
from .forms import *


@login_required(login_url="/login/")
def index(request):
    context = {'segment': 'index'}

    html_template = loader.get_template('index.html')
    return HttpResponse(html_template.render(context, request))


def tasks_render(form, request, msg=None, error=None):
    user = request.user
    tasks_list = Task.objects.filter(user=user)
    forms_list = []
    for task in tasks_list:
        edit_form = TaskForm(user=user, instance=task)
        forms_list.append(edit_form)

    edit_tasks_list = zip(tasks_list, forms_list)
    context = {
        'segment': 'tasks',
        'edit_tasks_list': edit_tasks_list,
        'form': form,
        'msg': msg
    }
    return render(request, 'tasks.html', context)


@login_required(login_url="/login/")
def tasks(request):
    old_post = request.session.get('_old_post')
    form = TaskForm(old_post or None, user=request.user)
    request.session['_old_post'] = None
    return tasks_render(form=form, request=request)


@login_required(login_url="/login/")
def createTask(request):
    user = request.user
    form = TaskForm(request.POST, user=user)
    msg = None
    error = None
    if request.method == 'POST':
        if form.is_valid():
            form_data = form.cleaned_data
            try:
                task_count = form_data['task_count']
                for i in range(0, task_count):
                    task = Task.objects.create_task(
                        store_name=form_data['store_name'],
                        shoe_size=form_data['shoe_size'] or -1,
                        sku_link=form_data['sku_link'],
                        proxy_list_id=form_data['proxy_list'].id if form_data['proxy_list'] is not None else None,
                        profile_id=form_data['profile'].id if form_data['profile'] is not None else None,
                        user_id=user.id
                    )
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
        request.session['_old_post'] = request.POST
    return redirect('tasks')


@login_required(login_url="/login/")
def updateTask(request, task_id):
    user = request.user
    msg = None
    error = None
    if request.method == 'POST':
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            error = 'error'
            msg = 'The task does not exist'
            messages.warning(request, msg)
        else:
            form = TaskForm(request.POST, user=user, instance=task)
            if form.is_valid():
                form_data = form.cleaned_data
                task.store_name = form_data['store_name']
                task.shoe_size = form_data['shoe_size'] or -1
                task.sku_link = form_data['sku_link']
                task.proxy_list_id = form_data['proxy_list'].id if form_data['proxy_list'] is not None else None
                task.profile_id = form_data['profile'].id if form_data['profile'] is not None else None
                try:
                    task.save()
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


@login_required(login_url='/login/')
def deleteTask(request, task_id):
    msg = None
    error = None
    try:
        task = Task.objects.get(id=task_id)
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


@login_required(login_url='/login/')
def clearTasks(request):
    error = None
    msg = None
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
            msg = 'Tasks deleted!'
            messages.warning(request, msg)

    return redirect('tasks')


@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]
        context['segment'] = load_template

        html_template = loader.get_template(load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:

        html_template = loader.get_template('page-500.html')
        return HttpResponse(html_template.render(context, request))
