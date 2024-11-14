// Function to refresh OS families, AMIs, and instance types for all blocks when region changes
function refreshAllFields() {
    const region = document.getElementById("region").value;
    if (!region) return;

    // Update OS families in all EC2 blocks
    document.querySelectorAll('select[name="os_family[]"]').forEach(osFamilySelect => {
        fetch(`/get_os_families?region=${region}`)
            .then(response => response.json())
            .then(data => {
                osFamilySelect.innerHTML = ""; // Clear current options
                osFamilySelect.appendChild(new Option("Select OS Family", ""));
                data.forEach(os => {
                    const option = document.createElement("option");
                    option.value = os;
                    option.textContent = os.charAt(0).toUpperCase() + os.slice(1);
                    osFamilySelect.appendChild(option);
                });
            });
    });

    // Update instance types in all EC2 blocks
    document.querySelectorAll('select[name="instance_type[]"]').forEach(instanceTypeSelect => {
        fetch(`/get_instance_types?region=${region}`)
            .then(response => response.json())
            .then(data => {
                instanceTypeSelect.innerHTML = ""; // Clear current options
                instanceTypeSelect.appendChild(new Option("Select Instance Type", ""));
                data.forEach(type => {
                    const option = document.createElement("option");
                    option.value = type;
                    option.textContent = type;
                    instanceTypeSelect.appendChild(option);
                });
            });
    });

    // Update AMIs in each EC2 block when OS family changes
    document.querySelectorAll('select[name="os_family[]"]').forEach(osFamilySelect => {
        osFamilySelect.addEventListener("change", function () {
            updateAMIs(osFamilySelect);
        });
    });
}

// Function to update AMIs based on selected OS family and global region
function updateAMIs(osFamilySelect) {
    const region = document.getElementById("region").value;
    const osFamily = osFamilySelect.value;
    const amiSelect = osFamilySelect.parentElement.querySelector('select[name="ami[]"]');

    if (!region || !osFamily) return;

    fetch(`/get_amis?region=${region}&os_family=${osFamily}`)
        .then(response => response.json())
        .then(data => {
            amiSelect.innerHTML = ""; // Clear current options
            amiSelect.appendChild(new Option("Select AMI", ""));
            data.forEach(ami => {
                const option = document.createElement("option");
                option.value = ami.id;
                option.textContent = `${ami.description} (${ami.id})`;
                amiSelect.appendChild(option);
            });
        });
}

// Function to dynamically add new sections for each resource type with a remove button
function showSection(sectionId) {
    const container = document.getElementById('dynamicSectionContainer');

    if (sectionId === 'ec2Section') {
        const newEC2Section = document.createElement('div');
        newEC2Section.className = 'form-section';
        newEC2Section.innerHTML = `
            <h2>EC2 Configuration</h2>
            <label for="resource_name">Resource Name:</label>
            <input type="text" name="resource_name[]" required><br>

            <label for="os_family">OS Family:</label>
            <select name="os_family[]" onchange="updateAMIs(this)" required>
                <option value="">Select OS Family</option>
            </select><br>

            <label for="ami">AMI:</label>
            <select name="ami[]" required>
                <option value="">Select AMI</option>
            </select><br>

            <label for="instance_type">Instance Type:</label>
            <select name="instance_type[]" required>
                <option value="">Select Instance Type</option>
            </select><br>

            <label for="storage_size">Storage Size (GB):</label>
            <input type="number" name="storage_size[]" min="0"><br>

            <label for="instance_count">Number of Instances:</label>
            <input type="number" name="instance_count[]" min="1" value="1" required><br>

            <h4>EC2 Tags</h4>
            <button type="button" onclick="addTag(this, 'ec2')">Add Tag</button>
            <div class="tag-inputs"></div>

            <br><button type="button" onclick="removeSection(this)">Remove</button><br>
        `;
        container.appendChild(newEC2Section);
        refreshAllFields(); // Refresh fields in the new block
    } else if (sectionId === 'vpcSection') {
        const newVPCSection = document.createElement('div');
        newVPCSection.className = 'form-section';
        newVPCSection.innerHTML = `
            <h2>VPC Configuration</h2>
            <label for="vpc_name">VPC Name:</label>
            <input type="text" name="vpc_name[]" required><br>

            <label for="vpc_cidr">CIDR Block:</label>
            <input type="text" name="vpc_cidr[]" placeholder="10.0.0.0/16" required><br>

            <h4>VPC Tags</h4>
            <button type="button" onclick="addTag(this, 'vpc')">Add Tag</button>
            <div class="tag-inputs"></div>

            <br><button type="button" onclick="removeSection(this)">Remove</button><br>
        `;
        container.appendChild(newVPCSection);

    } else if (sectionId === 's3Section') {
        const newS3Section = document.createElement('div');
        newS3Section.className = 'form-section';
        newS3Section.innerHTML = `
            <h2>S3 Bucket Configuration</h2>
            <label for="bucket_name">Bucket Name:</label>
            <input type="text" name="bucket_name[]" required><br>

            <label for="versioning">Enable Versioning:</label>
            <input type="checkbox" name="versioning[]"><br>

            <h4>S3 Tags</h4>
            <button type="button" onclick="addTag(this, 's3')">Add Tag</button>
            <div class="tag-inputs"></div>

            <br><button type="button" onclick="removeSection(this)">Remove</button><br>
        `;
        container.appendChild(newS3Section);
    }
}

// Function to add a new tag input (Name/Value pair) with resource-specific names
function addTag(button, resource) {
    const tagInputs = button.parentElement.querySelector('.tag-inputs');
    const tagDiv = document.createElement('div');
    tagDiv.className = 'tag-pair';
    tagDiv.innerHTML = `
        <input type="text" name="${resource}_tag_keys[]" placeholder="Name" required>
        <input type="text" name="${resource}_tag_values[]" placeholder="Value" required>
        <button type="button" onclick="removeTag(this)">Remove</button>
    `;
    tagInputs.appendChild(tagDiv);
}

// Function to remove a specific tag input pair
function removeTag(button) {
    button.parentElement.remove();
}

// Function to remove a specific section
function removeSection(button) {
    button.parentElement.remove();
}

document.addEventListener("DOMContentLoaded", function() {
    // Refresh fields across all blocks when the region changes
    document.getElementById("region").addEventListener("change", refreshAllFields);
});