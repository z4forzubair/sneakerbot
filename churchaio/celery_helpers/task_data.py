from churchaio.models import Task


def get_task_model(task, task_attr):
    task_attr["shoe_size"] = task.shoe_size
    task_attr["sku_link"] = task.sku_link


def get_profile_model(task, task_attr):
    task_attr["first_name"] = task.profile.first_name
    task_attr["last_name"] = task.profile.last_name
    task_attr["email"] = task.profile.email
    task_attr["salutation"] = task.profile.salutation
    task_attr["contact"] = task.profile.contact
    task_attr["dob_day"] = task.profile.day
    task_attr["dob_month"] = task.profile.month
    task_attr["dob_year"] = task.profile.year


def get_address_model(task, task_attr):
    task_attr["address1"] = task.profile.address.address1
    task_attr["address2"] = task.profile.address.address1
    task_attr["city"] = task.profile.address.city
    task_attr["country"] = task.profile.address.country
    task_attr["state"] = task.profile.address.state
    task_attr["postal_code"] = task.profile.address.postal_code


def get_payment_model(task, task_attr):
    task_attr["cc_number"] = task.profile.payment.cc_number
    task_attr["cc_expiry"] = task.profile.payment.cc_expiry
    task_attr["cc_code"] = task.profile.payment.cc_code


def get_task_attr(task_id):
    task_attr = {}
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        msg = "Some error occurred"
        # to do something if task not found here
        return None
    else:
        get_task_model(task, task_attr)
        get_profile_model(task, task_attr)
        get_address_model(task, task_attr)
        get_payment_model(task, task_attr)
    return task_attr
