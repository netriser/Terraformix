resource "aws_instance" "{{ resource_name }}" {
  ami           = "{{ ami_id }}"
  instance_type = "{{ instance_type }}"
  count         = {{ instance_count }}
  tags          = {{ tags }}
  {% if storage_size %}
  root_block_device {
    volume_size = {{ storage_size }}
  }
  {% endif %}
}

