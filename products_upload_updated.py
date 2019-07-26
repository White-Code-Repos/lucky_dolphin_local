import base64
import xmlrpc.client
import csv
import os

url = "http://197.51.64.243"
db = "Lucky_Live"
username = 'admin'
password = 'Access@2019'

# Authenticate admin user
common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
uid = common.authenticate(db, username, password, {})

models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))


def create_category(name, parent_id=False):
    cat_id = models.execute_kw(db, uid, password, 'product.category', 'create', [{
        'name': name,
        'parent_id': parent_id
    }])
    return cat_id


# Create Products
categories = {}
missed = []
# Load csv file
with open('IMPA7_MTMLUoM_updated_1901.csv') as csv_file:
    reader = csv.reader(csv_file)
    for i, col in enumerate(reader):
        if i == 0:
            continue
        print("Creating product: ", i, end=" ... ")
        level1, level2, level3 = col[:3]

        level1_full_name = level1.strip()
        if level1 not in categories:
            categories[level1_full_name] = create_category(level1_full_name)

        level2_full_name = "{}/{}".format(level1_full_name, level2.strip())
        if level2_full_name not in categories:
            categories[level2_full_name] = create_category(level2.strip(), categories[level1_full_name])

        level3_full_name = "{}/{}".format(level2_full_name, level3.strip())
        if level3_full_name not in categories:
            categories[level3_full_name] = create_category(level3.strip(), categories[level2_full_name])
        image = ""
        if col[8].lower().endswith("jpg"):
            path = "Pictures/Sec {}/{}".format(col[8][:2], col[8].lower())
            if os.path.isfile(path):
                with open(path, 'rb') as f:
                    image = f.read()
                    image = base64.encodebytes(image).decode()
            else:
                print("Failed to find : ", col[8])
                missed.append(col[8])
        data = {
            'id' : col[3]
            'categ_id': categories[level3_full_name],
            'default_code': col[3],
            'name': col[4],
            'description': col[7],
            'description_sale': col[4],
            'description_purchase': col[4],
            'uom_id': col[5],
            'uom_po_id': col[6],
            'image': image,
            'taxes_id': '',
            'supplier_taxes_id': '',
            'type': 'product'
        }
        product_id = models.execute_kw(db, uid, password, 'product.template', 'create', [data])
        print("created with id: ", product_id)
        print("Successful By Mostafa Abd El Fattah :)")
