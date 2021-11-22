from churchaio.models import Task


def get_task_model(task, task_attr):
    task_attr["shoe_size"] = task.shoe_size
    task_attr["sku_link"] = task.sku_link


def get_profile_model(task, task_attr):
    task_attr["first_name"] = task.profile.first_name
    task_attr["last_name"] = task.profile.last_name
    task_attr["email"] = task.profile.email
    task_attr["salutation"] = task.profile.salutation
    task_attr["contact"] = task.profile.contact.raw_input
    if len(str(task.profile.day)) == 1:
        task_attr["dob_day"] = '0' + str(task.profile.day)
    else:
        task_attr["dob_day"] = str(task.profile.day)
    if len(str(task.profile.month)) == 1:
        task_attr["dob_month"] = '0' + str(task.profile.month)
    else:
        task_attr["dob_month"] = str(task.profile.month)
    task_attr["dob_year"] = str(task.profile.year)


def get_address_model(task, task_attr):
    task_attr["address1"] = task.profile.address.address1
    task_attr["address2"] = task.profile.address.address2
    task_attr["city"] = task.profile.address.city
    task_attr["country"] = task.profile.address.country
    task_attr["state"] = task.profile.address.state
    task_attr["postal_code"] = str(task.profile.address.postal_code)


def get_payment_model(task, task_attr):
    task_attr["cc_number"] = task.profile.payment.cc_number
    if len(str(task.profile.payment.cc_expiry.month)) == 1:
        task_attr["month"] = '0' + str(task.profile.payment.cc_expiry.month)
    else:
        task_attr["month"] = str(task.profile.payment.cc_expiry.month)
    task_attr["year"] = str(task.profile.payment.cc_expiry.year)[-2:]
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
