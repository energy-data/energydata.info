import ckan.plugins.toolkit as tk
import ckan.lib.navl.dictization_functions as df

StopOnError = df.StopOnError


def not_both_empty(other_key, other_key_displayable):

    def callable(key, data, errors, context):

        value = data.get(key)
        other_value = data.get(key[:-1] + (other_key,))
        if not (value or other_value):
            errors[key].append(
                tk._('Missing value (alternatively specify a %s)')
                % other_key_displayable)
            raise StopOnError

    return callable

def year(key, data, errors, context):
    import re

    value = data.get(key) or ''
    if not value:
        return
    value = data[key] = value.strip()
    match = re.match('^(\d{4})$', value)
    if not match:
        errors[key].append(
            tk._('Bad year format. Must be: YYYY'))
        raise StopOnError
    year_int = int(match.groups()[0])
    if year_int < 1000 or year_int > 3000:
        errors[key].append(
            tk._('Bad year. Must be between 1000 and 3000.'))
        raise StopOnError

def yyyy_or_dd_mon_yyyy(key, data, errors, context):
    import re
    import datetime

    value = data.get(key) or ''
    if not value:
        return
    value = value.strip()

    # try as year
    match = re.match('^(\d{4})$', value)
    if match:
        year_int = int(match.groups()[0])
        if year_int < 1000 or year_int > 3000:
            errors[key].append(
                tk._('Bad year. Must be between 1000 and 3000.'))
            raise StopOnError
        data[key] = value
    else:
        # try as dd-mon-yyyy
        try:
            date = datetime.datetime.strptime(value, '%d-%b-%Y')
        except ValueError:
            errors[key].append(
                tk._('Bad date format. Must be: YYYY or DD-MON-YYYY'))
            raise StopOnError
        try:
            data[key] = date.strftime('%d-%b-%Y')  # reformat
        except ValueError:
            # can happen for years before 1900 - fine to ignore
            pass

def max_items(max_num):

    def callable(key, data, errors, context):

        value = data.get(key) or []
        # if it is one item, it doesn't arrive as a list
        if isinstance(value, list) and len(value) > max_num:
            errors[key].append(
                tk._('Too many items. The maximum is {}.').format(max_num))
            raise StopOnError

    return callable
