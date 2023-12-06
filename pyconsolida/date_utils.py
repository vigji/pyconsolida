from dateutil.relativedelta import relativedelta
from datetime import datetime


def data_from_commessa_folder(folder):
    """Read year and month from folder and generate a datetime object."""

    anno = int(folder.parent.parent.name)
    mese_raw = folder.parent.name.replace(" ", "_").split("_")[-1].lower()
    mese_map = dict(zip(
        ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno",
         "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"],
        range(1, 13)
    ))
    mese = mese_map[mese_raw]

    return datetime(anno, mese, 1)


def months_between_dates(date1, date2):
    """Date difference in number of months."""
    date_diff = relativedelta(date1, date2)
    return date_diff.months + date_diff.years * 12


def months_from_start(folder_list):
    """For every folder, count months from the first time it was seen."""
    all_months = [data_from_commessa_folder(folder) for folder in folder_list]
    all_months = sorted(all_months)
    print(all_months)
    return [months_between_dates(month, all_months[0]) for month in all_months]
