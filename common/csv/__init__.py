import csv
from ..models import AdministrativeLvl1, AdministrativeLvl2, AdministrativeLvl3, AdministrativeLvl4


def import_provinces_from_csv(filename='common/csv/provinces.csv'):
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            # We're only interested in the second item in each row for the name
            AdministrativeLvl1.objects.create(id=row[0], name=row[1])
    print("Imported provinces successfully!")

def import_regencies_from_csv(filename='common/csv/regencies.csv'):
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            # Fetch the AdministrativeLvl1 instance based on the ID from the CSV
            lvl1_instance = AdministrativeLvl1.objects.get(id=row[1])
            
            # Create an AdministrativeLvl2 instance with the fetched lvl1_instance and the name from the CSV
            AdministrativeLvl2.objects.create(id=row[0], lvl1=lvl1_instance, name=row[2])

    print("Imported regencies successfully!")

def import_districts_from_csv(filename='common/csv/districts.csv'):
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            # Fetch the AdministrativeLvl2 instance based on the ID from the CSV
            lvl2_instance = AdministrativeLvl2.objects.get(id=row[1])
            
            # Create an AdministrativeLvl3 instance with the fetched lvl2_instance and the name from the CSV
            AdministrativeLvl3.objects.create(id=row[0], lvl2=lvl2_instance, name=row[2])

    print("Imported districts successfully!")

def import_villages_from_csv(filename='common/csv/villages.csv'):
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            # Fetch the AdministrativeLvl3 instance based on the ID from the CSV
            lvl3_instance = AdministrativeLvl3.objects.get(id=row[1])
            
            # Create an AdministrativeLvl4 instance with the fetched lvl2_instance and the name from the CSV
            try:
                AdministrativeLvl4.objects.get_or_create(id=row[0], lvl3=lvl3_instance, name=row[2])
            except:
                AdministrativeLvl4.objects.get_or_create(id=row[0]+"1111", lvl3=lvl3_instance, name=row[2])


    print("Imported vallages successfully!")

def generate_administratives():
    import_provinces_from_csv()
    import_regencies_from_csv()
    import_districts_from_csv()
    import_villages_from_csv()