def is_admin_or_staff(user):
    return user.is_staff or user.is_superuser
