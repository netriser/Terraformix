resource "aws_s3_bucket" "{{ bucket_name }}" {
  bucket = "{{ bucket_name }}"

  versioning {
    enabled = {{ versioning_enabled }}
  }

  tags = {{ tags }}
}

