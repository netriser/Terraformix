resource "aws_vpc" "{{ vpc_name }}" {
  cidr_block = "{{ cidr_block }}"
  tags       = {{ tags }}
}

