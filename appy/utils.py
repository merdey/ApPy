from appy.models import Application


def apply_for_position(position, user):
    app = Application(user=user, position=position)
    app.save()