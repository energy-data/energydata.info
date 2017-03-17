import ckan.plugins.toolkit as toolkit

log = __import__('logging').getLogger(__name__)

country_vocab = 'country_names'

def country_names():
    import pycountry

    # Create the tag vocabulary if it doesn't exist
    user = toolkit.get_action('get_site_user')({'ignore_auth': True}, {})
    context = {'user': user['name']}
    try:  # Check if the vocab exists
        data = {'id': country_vocab}
        toolkit.get_action('vocabulary_show')(context, data)
    except toolkit.ObjectNotFound:  # It doesn't exist, create the vocab
        data = {'name': country_vocab}
        vocab = toolkit.get_action('vocabulary_create')(context, data)
        country_names = [country.alpha_3
                         for country in list(pycountry.countries)]
        for name in country_names:
            data = {'name': name, 'vocabulary_id': vocab['id']}
            toolkit.get_action('tag_create')(context, data)

    try:
        countries = toolkit.get_action('tag_list')(
            data_dict={'vocabulary_id': country_vocab})
        return countries
    except toolkit.ObjectNotFound:
        log.debug('Could not find vocabulary')

def country_code_to_name(country_code):
    import pycountry
    return pycountry.countries.get(alpha_3=country_code).name

def country_options():
    return [{'name': country_code_to_name(country_code), 'value': country_code}
            for country_code in country_names()]


region_vocab = 'regions'

def regions_data():
    return dict(
        AFR='Africa',
        EAP='East Asia and Pacific',
        ECA='Europe and Central Asia',
        LCR='Latin America & Caribbean',
        SAR='South Asia',
        MNA='Middle East and North Africa',
    )

def regions():
    # Create the vocabulary if it doesn't exist
    user = toolkit.get_action('get_site_user')({'ignore_auth': True}, {})
    context = {'user': user['name']}
    try:  # Check if the vocab exists
        data = {'id': region_vocab}
        toolkit.get_action('vocabulary_show')(context, data)
    except toolkit.ObjectNotFound:  # It doesn't exist, create the vocab
        data = {'name': region_vocab}
        vocab = toolkit.get_action('vocabulary_create')(context, data)
        for name in regions_data().keys():
            data = {'name': name, 'vocabulary_id': vocab['id']}
            toolkit.get_action('tag_create')(context, data)

    try:
        regions = toolkit.get_action('tag_list')(
            data_dict={'vocabulary_id': region_vocab})
        return regions
    except toolkit.ObjectNotFound:
        log.debug('Could not find vocabulary')


def region_code_to_name(region_code):
    return regions_data().get(region_code, '')

def region_options():
    regions_dict = regions_data()
    return [{'name': regions_dict[region_code], 'value': region_code}
            for region_code in regions()]


topic_vocab = 'topics'

def topics():
    # Create the vocabulary if it doesn't exist
    user = toolkit.get_action('get_site_user')({'ignore_auth': True}, {})
    context = {'user': user['name']}
    try:  # Check if the vocab exists
        data = {'id': topic_vocab}
        toolkit.get_action('vocabulary_show')(context, data)
    except toolkit.ObjectNotFound:  # It doesn't exist, create the vocab
        data = {'name': topic_vocab}
        vocab = toolkit.get_action('vocabulary_create')(context, data)
        topics = '''
Energy demand
Energy efficiency
Renewable energy
Energy access
Resource assessments
Measurement stations
Power system and utilities
Transmission and distribution
Pipeline networks
Physical features
Boundaries
Extractive industries
Project sites
Climate
Demographics
Surveys
Economics and prices
Policies and plans
Information technology
Environment
Transport
Water
Agriculture
Bioenergy
Geothermal
Hydropower
Solar
Wind
Thermal power'''.strip().split('\n')
        for name in topics:
            data = {'name': name, 'vocabulary_id': vocab['id']}
            toolkit.get_action('tag_create')(context, data)

    try:
        topics = toolkit.get_action('tag_list')(
            data_dict={'vocabulary_id': topic_vocab})
        return topics
    except toolkit.ObjectNotFound:
        log.debug('Could not find vocabulary')

def topic_options():
    return [{'name': topic, 'value': topic} for topic in topics()]


status_vocab = 'statuses'

def statuses():
    return '''
Complete
Obsolete
Ongoing
Planned
Required
Under Development
    '''.strip().split('\n')

def status_options():
    return [{'name': status, 'value': status}
            for status in [''] + statuses()]
