# myturn
Automate scheduling an appointment on myturn.ca.gov

To run this program, run add a config.yaml file (see below for format) and run `make run`

```
chromedriver_location: "C:\\chromedriver_win32\\chromedriver"

eligibility:
  # Starting age ranges (16, 50, 65, 75)
  age_range: ""
  health_condition: ""
  disability: ""
  industry: ""
  county: ""

locations:
  - 12345

personal_info:
  name: ""
  DOB: MM/DD/YYYY
  mother: ""
  gender: ""
  race: ""
  ethnicity: ""
  email: ""
  mobile: (123) 456-7890
  address: ""
  city: ""
  zip_code: 12345
  industry: ""
  primary_carrier: ""
  policy_number: ""
```