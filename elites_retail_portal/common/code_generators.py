"""Code generators."""

import time


def check_fail_unique_product_code(self, product_code):
    """Validate that product_code is unique."""
    check_fail = False
    if self.__class__.objects.filter(product_code=product_code).exists():
        check_fail = True

    return check_fail


def generate_product_code_id(self, item, ignore_code_ids):
    """Generate an item code."""
    id = 1
    product_exists = self.__class__.objects.filter(
        inventory=self.inventory).exists()

    if product_exists:
        count = self.__class__.objects.filter(
            inventory=self.inventory).count()
        last = self.__class__.objects.filter(
            inventory=self.inventory).order_by('created_on')[count-1]
        last_product_code = last.product_code
        last_product_code_id = int(last_product_code.split('/')[2])
        id += last_product_code_id

    for code_id in ignore_code_ids:
        if id == int(code_id):
            id = id + 1

    code = ''
    if id < 10:
        code = '0{}'.format(id)
    else:
        code = str(id)

    return code


def abbreviate_name(name):
    """Abbreviate any name."""
    name_values = name.split()
    name_abbrv = ''
    if name_values != []:
        for value in name_values:
            name_abbrv += value[0].upper()

    return name_abbrv


def generate_branch_code():
    """Generate a code for a enterprise's branch."""
    code = '01'
    return code


def get_enterprise_abbreviations(object):
    """Generate an abbreviation to the enterprise."""
    enterprise_abbrv = abbreviate_name(object.name)
    if object.is_main_branch:
        return enterprise_abbrv, 'MB', '01'

    else:
        # GET NAME OF BRANCH LOCATION
        branch_abbrv = 'OB'
        branch_code = generate_branch_code()
        return enterprise_abbrv, branch_abbrv, branch_code


def return_year_and_id(id):
    """Return year and id."""
    year = time.strftime("%y")
    id += int(year+'00')

    return id


def generate_enterprise_code_id(object):
    """Generate enterprise code id."""
    id = 1
    enterprise_exists = object.__class__.objects.all().exists()

    if not enterprise_exists:
        return return_year_and_id(id)

    # count = object.__class__.objects.all().count()
    last_enterprise_code = object.__class__.objects.all().latest(
        'created_on').enterprise_code
    last_enterprise_code = int(last_enterprise_code.split('/')[2].split('-')[0])
    id += last_enterprise_code

    return id


def generate_section_code_id(object):
    """Generate section code id."""
    id = 1
    enterprise_exists = object.__class__.objects.all().exists()

    if not enterprise_exists:
        return return_year_and_id(id)

    count = object.__class__.objects.all().count()
    last_section_code = object.__class__.objects.all().order_by(
        'created_on')[count-1].section_code
    last_section_code = int(last_section_code.split('/')[2])
    id += last_section_code

    return id


def generate_type_code_id(object):
    """Generate type code id."""
    id = 1
    enterprise_exists = object.__class__.objects.all().exists()

    if not enterprise_exists:
        return return_year_and_id(id)

    count = object.__class__.objects.all().count()
    last_type_code = object.__class__.objects.all().order_by(
        'created_on')[count-1].type_code
    last_type_code = int(last_type_code.split('/')[2])
    id += last_type_code

    return id


def generate_category_code_id(object):
    """Generate Category code id."""
    id = 1
    enterprise_exists = object.__class__.objects.all().exists()

    if not enterprise_exists:
        return return_year_and_id(id)

    count = object.__class__.objects.all().count()
    last_category_code = object.__class__.objects.all().order_by(
        'created_on')[count-1].category_code
    last_category_code = int(last_category_code.split('/')[2])
    id += last_category_code

    return id


def generate_brand_code_id(object):
    """Generate brand code id."""
    id = 1
    enterprise_exists = object.__class__.objects.all().exists()

    if not enterprise_exists:
        return return_year_and_id(id)

    count = object.__class__.objects.all().count()
    last_brand_code = object.__class__.objects.all().order_by(
        'created_on')[count-1].brand_code
    last_brand_code = int(last_brand_code.split('/')[2])
    id += last_brand_code

    return id


def generate_model_code_id(object):
    """Generate model code id."""
    id = 1
    enterprise_exists = object.__class__.objects.all().exists()

    if not enterprise_exists:
        return return_year_and_id(id)

    count = object.__class__.objects.all().count()
    last_model_code = object.__class__.objects.all().order_by(
        'created_on')[count-1].model_code
    last_model_code = int(last_model_code.split('/')[2])
    id += last_model_code

    return id


def generate_item_code_id(object):
    """Generate item code id."""
    id = 1
    enterprise_exists = object.__class__.objects.all().exists()

    if not enterprise_exists:
        return return_year_and_id(id)

    count = object.__class__.objects.all().count()
    last_item_code = object.__class__.objects.all().order_by(
        'created_on')[count-1].item_code
    last_item_code = int(last_item_code.split('/')[2])
    id += last_item_code

    return id


def generate_units_code_id(object):
    """Generate units code id."""
    id = 1
    enterprise_exists = object.__class__.objects.all().exists()

    if not enterprise_exists:
        return return_year_and_id(id)

    count = object.__class__.objects.all().count()
    last_units_code = object.__class__.objects.all().order_by(
        'created_on')[count-1].units_code
    last_units_code = int(last_units_code.split('/')[2])
    id += last_units_code

    return id


def get_enterprise_code(object):
    """Get enterprise code."""
    try:
        enterprise_code = object.enterprise.split('/')[1]
    except IndexError:
        enterprise_code = object.enterprise[0]

    return enterprise_code


def generate_enterprise_code(object):
    """Auto generate elites code."""
    if object.__class__.__name__ == "Enterprise":
        enterprise_abbrv, brach_abbrv, branch_code = get_enterprise_abbreviations(object)
        enterprise_code_id = generate_enterprise_code_id(object)
        enterprise_code = 'EAL-E/{}-{}/{}-{}'.format(
            enterprise_abbrv, brach_abbrv, enterprise_code_id, branch_code)

        return enterprise_code

    if object.__class__.__name__ == "Section":
        enterprise_code = get_enterprise_code(object)
        section_abbrv = abbreviate_name(object.section_name)
        section_code_id = generate_section_code_id(object)
        section_code = '{}/S-{}/{}'.format(
            enterprise_code, section_abbrv, section_code_id)

        return section_code

    if object.__class__.__name__ == "Category":
        enterprise_code = get_enterprise_code(object)
        category_abbrv = abbreviate_name(object.category_name)
        category_code_id = generate_category_code_id(object)
        category_code = '{}/C-{}/{}'.format(
            enterprise_code, category_abbrv, category_code_id)

        return category_code

    if object.__class__.__name__ == "ItemType":
        enterprise_code = get_enterprise_code(object)
        item_type_abbrv = abbreviate_name(object.type_name)
        type_code_id = generate_type_code_id(object)
        type_code = '{}/T-{}/{}'.format(
            enterprise_code, item_type_abbrv, type_code_id)

        return type_code

    if object.__class__.__name__ == "Brand":
        enterprise_code = get_enterprise_code(object)
        brand_abbrv = abbreviate_name(object.brand_name)
        brand_code_id = generate_brand_code_id(object)
        brand_code = '{}/B-{}/{}'.format(
            enterprise_code, brand_abbrv, brand_code_id)

        return brand_code

    if object.__class__.__name__ == "ItemModel":
        enterprise_code = get_enterprise_code(object)
        model_abbrv = abbreviate_name(object.model_name)
        model_code_id = generate_model_code_id(object)
        model_code = '{}/M-{}/{}'.format(
            enterprise_code, model_abbrv, model_code_id)

        return model_code

    if object.__class__.__name__ == "Item":
        enterprise_code = get_enterprise_code(object)
        item_abbrv = abbreviate_name(object.item_name)
        item_code_id = generate_item_code_id(object)
        item_code = '{}/I-{}/{}'.format(
            enterprise_code, item_abbrv, item_code_id)

        return item_code

    if object.__class__.__name__ == "Units":
        enterprise_code = get_enterprise_code(object)
        units_abbrv = abbreviate_name(object.units_name)
        units_code_id = generate_units_code_id(object)
        units_code = '{}/U-{}/{}'.format(
            enterprise_code, units_abbrv, units_code_id)

        return units_code
