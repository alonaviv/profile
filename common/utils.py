
def get_teacher_object(request):
    user = request.user
    if hasattr(user, 'teacher'):
        return user.teacher

