from . import db  # From current package ("website") import db
from .models import DataSet
from .predefined_data_json import pd, primary_energy_use, fmt
from .util_web import string_to_csv

def add_predefined():

    # First delete all public (non-user) datasets
    try:
        # foo = DataSet.query.filter(DataSet.user_id is None).first_or_404()
        # print(foo.label)

        num_rows_deleted = DataSet.query.filter(DataSet.user_id == None).delete()
        db.session.commit()
        print(f"Deleted {num_rows_deleted} datasets.")
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting non-user datasets: {e}")

    added_datasets = []

    # Add categories with subcategories OECD, BRICS, Rest, and World
    for key in pd:
        time_values = pd[key]['time_values']
        data_unit = pd[key]['data_unit']
        if 'data_scale' not in pd[key]:
            print(f"NO data_scale in pd[{key}]")
        data_scale = pd[key]['data_scale']
        description = pd[key]['description']

        for subkey in ['oecd', 'brics', 'rest', 'world']:
            label = pd[key][subkey]['label']
            data_values = pd[key][subkey]['data_values']
            legend = pd[key][subkey]['legend']
            dataset = DataSet(id_predef='predef' + str(len(added_datasets) + 1),
                              label=label,
                              description=description,
                              time_values=string_to_csv(time_values),
                              data_values=string_to_csv(data_values),
                              legend=legend,
                              data_unit=data_unit,
                              data_scale=data_scale)
            db.session.add(dataset)
            added_datasets.append(dataset)

    # Primary energy use
    dataset = DataSet(id_predef='predef' + str(len(added_datasets) + 1),
                      label=primary_energy_use['label'],
                      description=primary_energy_use['description'],
                      time_values=primary_energy_use['time_values'],
                      data_values=primary_energy_use['data_values'],
                      legend=primary_energy_use['legend'],
                      data_unit=primary_energy_use['data_unit'],
                      data_scale=primary_energy_use['data_scale'])
    db.session.add(dataset)
    added_datasets.append(dataset)

    # FMT
    dataset = DataSet(id_predef='predef' + str(len(added_datasets) + 1),
                      label=fmt['label'],
                      description=fmt['description'],
                      time_values=fmt['time_values'],
                      data_values=fmt['data_values'],
                      legend=fmt['legend'],
                      data_unit=fmt['data_unit'],
                      data_scale=fmt['data_scale'],
                      data_is_qualitative=fmt['data_is_qualitative'])
    db.session.add(dataset)
    added_datasets.append(dataset)

    db.session.commit()

    # id = db.Column(db.Integer, primary_key=True)
    # label = db.Column(db.String(LABEL_MAXLENGTH), unique=True)   # For checkbox lists
    # description = db.Column(db.String(DESCRIPTION_MAXLENGTH))
    # time_values = db.Column(db.String(DATA_MAXLENGTH))
    # data_values = db.Column(db.String(DATA_MAXLENGTH))
    # legend = db.Column(db.String(LABEL_MAXLENGTH))
    # data_unit = db.Column(db.String(UNIT_MAXLENGTH))
    # date = db.Column(db.DateTime(timezone=True), default=func.now())
    # user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # null means predefined data
