from flask import Flask, render_template, request, jsonify
import sqlite3
import json

app = Flask(__name__)
DATABASE = 'aws_data.db'

# Helper functions for database queries
def query_db(query, args=(), single=False):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(query, args)
    rv = cursor.fetchall()
    conn.close()
    return (rv[0] if rv else None) if single else rv

def fetch_single_column(query, args=()):
    return [row[0] for row in query_db(query, args)]

# Routes to query data from the SQLite database instead of AWS

@app.route('/get_regions')
def get_regions():
    regions = fetch_single_column("SELECT region_name FROM regions ORDER BY region_name ASC")
    return jsonify(regions)

@app.route('/get_instance_types')
def get_instance_types():
    region = request.args.get('region')
    instance_types = fetch_single_column(
        "SELECT instance_type FROM instance_types WHERE region_name = ? ORDER BY instance_type ASC", 
        (region,)
    )
    return jsonify(instance_types)

@app.route('/get_os_families')
def get_os_families():
    os_families = ['ubuntu', 'windows', 'amzn', 'rhel']  # Static list of OS families
    return jsonify(os_families)

@app.route('/get_amis')
def get_amis():
    region = request.args.get('region')
    os_family = request.args.get('os_family')
    query = """
        SELECT ami_id, description 
        FROM amis 
        WHERE region_name = ? AND description LIKE ? 
        ORDER BY description ASC
    """
    amis = [{"id": row[0], "description": row[1]} for row in query_db(query, (region, f"{os_family}%"))]
    return jsonify(amis)

# Route to generate the Terraform configurations based on form input
@app.route('/generate', methods=['POST'])
def generate_template():
    terraform_code = ""

    # EC2 Configurations
    ec2_names = request.form.getlist('resource_name[]')
    regions = request.form.getlist('region[]')
    instance_types = request.form.getlist('instance_type[]')
    amis = request.form.getlist('ami[]')
    storage_sizes = request.form.getlist('storage_size[]')
    instance_counts = request.form.getlist('instance_count[]')
    ec2_tags = request.form.getlist('ec2_tags[]')

    for i in range(len(ec2_names)):
        ec2_config = {
            "resource_name": ec2_names[i],
            "region": regions[i],
            "instance_type": instance_types[i],
            "ami_id": amis[i],
            "storage_size": storage_sizes[i] if storage_sizes[i] else None,
            "instance_count": instance_counts[i] if instance_counts[i] else 1,
            "tags": json.loads(ec2_tags[i]) if ec2_tags[i] else {}
        }
        terraform_code += render_template('ec2.tf', **ec2_config)

    # VPC Configurations
    vpc_names = request.form.getlist('vpc_name[]')
    cidr_blocks = request.form.getlist('vpc_cidr[]')
    vpc_tags = request.form.getlist('vpc_tags[]')

    for i in range(len(vpc_names)):
        vpc_config = {
            "vpc_name": vpc_names[i],
            "cidr_block": cidr_blocks[i],
            "tags": json.loads(vpc_tags[i]) if vpc_tags[i] else {}
        }
        terraform_code += render_template('vpc.tf', **vpc_config)

    # S3 Configurations
    bucket_names = request.form.getlist('bucket_name[]')
    versioning_enabled = request.form.getlist('versioning[]')
    bucket_tags = request.form.getlist('bucket_tags[]')

    for i in range(len(bucket_names)):
        s3_config = {
            "bucket_name": bucket_names[i],
            "versioning_enabled": 'true' if i < len(versioning_enabled) and versioning_enabled[i] else 'false',
            "tags": json.loads(bucket_tags[i]) if bucket_tags[i] else {}
        }
        terraform_code += render_template('s3.tf', **s3_config)

    # Render the final Terraform code to output.html
    return render_template('output.html', terraform_code=terraform_code)

# Route to display form with AWS regions and instance types
@app.route('/')
def index():
    regions = fetch_single_column("SELECT region_name FROM regions ORDER BY region_name ASC")
    return render_template('index.html', regions=regions)

if __name__ == '__main__':
    app.run(debug=True)
