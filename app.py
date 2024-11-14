from flask import Flask, render_template, request, jsonify
import sqlite3
import os

app = Flask(__name__)
DATABASE = 'aws_data.db'

def query_db(query, args=(), single=False):
    """Execute a query and fetch results."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(query, args)
    rv = cursor.fetchall()
    conn.close()
    return (rv[0] if rv else None) if single else rv

def fetch_single_column(query, args=()):
    """Fetch a single column result from a query."""
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
    os_families = ['ubuntu', 'windows', 'amzn', 'rhel']  # Fixed list for simplicity
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

@app.route('/generate', methods=['POST'])
def generate_template():
    resource_name = request.form['resource_name']
    region = request.form['region']
    instance_type = request.form['instance_type']
    ami_id = request.form['ami']
    instance_count = int(request.form['instance_count'])
    
    # Get storage size input and validate if it is provided
    storage_size = request.form.get('storage_size')
    root_block_device = f"""
      root_block_device {{
        volume_size = {storage_size}
      }}
    """ if storage_size and storage_size.isdigit() and int(storage_size) > 0 else ""

    # Terraform template for a single or multiple instances
    terraform_template = f"""
    provider "aws" {{
      region = "{region}"
    }}

    resource "aws_instance" "{resource_name}" {{
      ami           = "{ami_id}"
      instance_type = "{instance_type}"
      {f'count = {instance_count}' if instance_count > 1 else ''}

      {root_block_device}

      tags = {{
        Name = "{resource_name}${{count.index + 1}}" if {instance_count > 1} else "{resource_name}"
      }}
    }}
    """

    # Render the generated template to a new HTML page
    return render_template('output.html', terraform_template=terraform_template)

# Route to display form with AWS regions and instance types
@app.route('/')
def index():
    regions = fetch_single_column("SELECT region_name FROM regions ORDER BY region_name ASC")
    return render_template('index.html', regions=regions)

if __name__ == '__main__':
    app.run(debug=True)
