from flask import redirect, url_for
from flask_login import login_required, current_user
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from .models import User, DBScript, Settings, SimulationTask
from . import db


# Base class for admin views
class LesimAdminModelView(ModelView):
    can_create = True        # Model creation allowed
    can_edit = True          # Allow editing records
    can_delete = True        # Model deletion allowed
    can_view_details = True  # Enable the Details view

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        # Redirect to landing page if user browses to a subpage to the admin endpoint
        return redirect(url_for('views.landing'))


# Admin view for the User model
class UserAdmin(LesimAdminModelView):
    column_list = (User.id, User.is_admin, User.username, User.email, User.password,
                   User.settings_id, User.simulation_task_id)
    form_columns = (User.is_admin, User.username, User.email, User.password)


# Admin view for the DBScript model
class DBScriptAdmin(LesimAdminModelView):
    column_list = (DBScript.id, DBScript.id_predef, DBScript.user_id,
                   DBScript.name, DBScript.code, DBScript.user_id)
    form_columns = (DBScript.name, DBScript.code)


# Admin view for the Settings model
class SettingsAdmin(LesimAdminModelView):
    pass


# Admin view for the SimulationTask model
class SimulationTaskAdmin(LesimAdminModelView):
    column_list = (SimulationTask.id, SimulationTask.message1, SimulationTask.progress1,
                   SimulationTask.is_done, SimulationTask.stop_clicked)
    form_columns = (SimulationTask.message1, SimulationTask.progress1,
                    SimulationTask.is_done, SimulationTask.stop_clicked)


def add_admin_views(app):
    admin = Admin(app, name='Admin', template_mode='bootstrap3')
    admin.add_view(UserAdmin(User, db.session))
    admin.add_view(DBScriptAdmin(DBScript, db.session, "DBScript"))  # "DBScript", Otherwise the displayed table name is "D B Script"
    admin.add_view(SettingsAdmin(Settings, db.session))
    admin.add_view(SimulationTaskAdmin(SimulationTask, db.session))
