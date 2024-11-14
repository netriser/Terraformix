import boto3
import sqlite3
import os

DATABASE = 'aws_data.db'

# Initialize AWS clients
ec2 = boto3.client('ec2')

def create_database():
    # Remove the existing database
    if os.path.exists(DATABASE):
        os.remove(DATABASE)
    
    # Create a new SQLite database and tables
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''CREATE TABLE regions (id INTEGER PRIMARY KEY, region_name TEXT UNIQUE)''')
    cursor.execute('''CREATE TABLE instance_types (id INTEGER PRIMARY KEY, region_name TEXT, instance_type TEXT)''')
    cursor.execute('''CREATE TABLE amis (id INTEGER PRIMARY KEY, region_name TEXT, ami_id TEXT, description TEXT)''')
    
    conn.commit()
    conn.close()

def populate_database():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Fetch and insert regions
    #regions = ec2.describe_regions(AllRegions=False)['Regions']
    regions = ['us-east-1', 'eu-west-1']
    for region in regions:
        #cursor.execute("INSERT INTO regions (region_name) VALUES (?)", (region['RegionName'],))
        cursor.execute("INSERT INTO regions (region_name) VALUES (?)", (region,))

    conn.commit()

    # Fetch and insert instance types, OS families, and AMIs for each region
    for region in regions:
         #region_name = region['RegionName']
        region_name = region
        # Fetch instance types
        ec2_region = boto3.client('ec2', region_name=region_name)
        paginator = ec2_region.get_paginator('describe_instance_types')
        instance_types = set()
        for page in paginator.paginate():
            for instance_type in page['InstanceTypes']:
                instance_types.add(instance_type['InstanceType'])
        
        for instance_type in instance_types:
            cursor.execute("INSERT INTO instance_types (region_name, instance_type) VALUES (?, ?)", (region_name, instance_type))

        # Fetch OS families and AMIs
        os_family = ['ubuntu','windows','amzn','rhel','redhat']
        images = ec2_region.describe_images(Owners=['amazon'])['Images']
        #os_families = set()
        for image in images:
            if any(x in image['Name'].lower() for x in os_family):    
                # Insert AMI for each OS family and region
                print(image['Name'])
                cursor.execute("INSERT INTO amis (region_name, ami_id, description) VALUES (?, ?, ?)", 
                            (region_name, image['ImageId'], image['Name']))
            
    conn.commit()
    conn.close()

# Initialize the database when the app starts
create_database()
populate_database()
