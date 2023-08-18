import enum
from sqlalchemy import Enum
from flask_login import UserMixin
from sqlalchemy.sql import func

from . import db  # From current package ("website") import db
from . import login_manager

from .global_variables import gvar


class DBScript(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_predef = db.Column(db.Integer, unique=True, nullable=True)  # Unique if not null
    name = db.Column(db.String(gvar['SCRIPTNAME_MAXLENGTH']))
    code = db.Column(db.String(gvar['CODE_MAXLENGTH']))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # null means predefined script


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    is_admin = db.Column(db.Boolean, default=False)
    email = db.Column(db.String(gvar['EMAIL_MAXLENGTH']), unique=True)
    password = db.Column(db.String(gvar['PASSWORD_MAXLENGTH']))
    username = db.Column(db.String(gvar['USERNAME_MAXLENGTH']))
    scripts = db.relationship('DBScript')
    settings_id = db.Column(db.Integer, db.ForeignKey('settings.id'), nullable=True, default=None)
    simulation_task_id = db.Column(db.Integer, db.ForeignKey('simulation_task.id'), nullable=True, default=None)


class PlotOrientation(enum.Enum):
    horizontal = 'horizontal'
    vertical = 'vertical'


class LegendOrientation(enum.Enum):
    h = 'h'  # Horizontal
    v = 'v'  # Vertical


class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plot_type = db.Column(db.String(5), default="plot")  # plot or image
    file_type_mpl = db.Column(db.String(3), default="png")
    file_type_plotly = db.Column(db.String(4), default="png")
    plot_orientation = db.Column(Enum(PlotOrientation), default=PlotOrientation.vertical)
    plot_width = db.Column(db.Integer, default=300)
    plot_height = db.Column(db.Integer, default=300)
    # legend_x = db.Column(db.Float, default=1)
    # legend_y = db.Column(db.Float, default=0)
    # legend_x_anchor = db.Column(db.String(6), default="right")  # left, center, or right
    # legend_y_anchor = db.Column(db.String(6), default="bottom")  # top, middle, or bottom
    legend_orientation = db.Column(Enum(LegendOrientation), default=LegendOrientation.v)
    paper_color = db.Column(db.String(7), default="#dfdfdf")  # hex color, e.g. #0cdf41
    plot_bgcolor = db.Column(db.String(7), default="#ffffff")  # hex color, e.g. #0cdf41
    keep_plots = db.Column(db.Boolean, default=False)

    def save(self, settings):
        for fn in settings:
            val = settings[fn]
            setattr(self, fn, val)

    def to_dict(self):
        out = dict()
        for fn in vars(self):
            if fn != '_sa_instance_state':
                val = getattr(self, fn)
                if isinstance(val, enum.Enum):
                   out[fn] = val.value 
                else:
                    out[fn] = val
        return(out)


class SimulationTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message1 = db.Column(db.String(50), default="")
    progress1 = db.Column(db.Double(), default=0)
    is_done = db.Column(db.Boolean, default=True)
    stop_clicked = db.Column(db.Boolean, default=False)


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))
