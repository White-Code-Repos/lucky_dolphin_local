import base64
import xmlrpc.client
import csv
import os

url = "http://localhost:8069"
db = "luck_test1"
username = 'admin'
password = 'iti'

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
with open('products.csv') as csv_file:
    reader = csv.reader(csv_file)
    for i, row in enumerate(reader):
        if i == 0:
            continue
        print("Creating product: ", i, end=" ... ")
        level1, level2, level3 = row[:3]

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
        if row[8].lower().endswith("jpg"):
            path = "/home/abdulrahman/Downloads/pictures/Pictures/Sec {}/{}".format(row[8][:2], row[8].lower())
            if os.path.isfile(path):
                with open(path, 'rb') as f:
                    image = f.read()
                    image = base64.encodebytes(image).decode()
            else:
                print("Failed to find : ", row[8])
                missed.append(row[8])
        data = {
            'categ_id': categories[level3_full_name],
            'default_code': row[3],
            'name': row[4],
            'description': row[7],
            'description_sale': row[7],
            'description_purchase': row[7],
            'image': image,
            'type': 'product'
        }
        product_id = models.execute_kw(db, uid, password, 'product.template', 'create', [data])
        print("created with id: ", product_id)

