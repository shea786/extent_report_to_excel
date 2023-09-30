# Convert ExtentReport to Excel Report

# Table of Contents
1. [How to use](#How-to-Use)

## How to Use
### Install requirements
```
pip install -r requirements.txt
```

### Setup Environment
Create a copy from `config/report_config.sample.ini`
```
cp config/report_config.sample.ini config/report_config.ini
```

Populate the config variables
```
filename - Name of the Extent Report HTML file
directory_to_search - Directory to search, ensure / is escapated
jira_project_key_prefix_for_tags - Project key for JIRA user stories and test cases
```

### Run the code
```
python run.py
```

### Output
This will create Excel and JSON report in the exported_data directory.
The output name will be the timestamp of the report
