import yaml

def get_config():
    return Config()

class Config:
    def __init__(self):
        with open("config.yaml") as f:
            self.config = yaml.load(f, Loader=yaml.SafeLoader)
        for k, v in self.config["eligibility"].items():
            setattr(self, str(k), v)
        for k, v in self.config["personal_info"].items():
            setattr(self, str(k), v)

    def get_locations(self):
        for location in self.config["locations"]:
            yield location

    @property
    def chromedriver_location(self):
        return self.config["chromedriver_location"]

    @property
    def first_name(self):
        return self.name.split()[0]
    
    @property
    def last_name(self):
        return self.name.split()[1]

    @property
    def dob_month(self):
        return self.DOB.split("/")[0]
    
    @property
    def dob_day(self):
        return self.DOB.split("/")[1]

    @property
    def dob_year(self):
        return self.DOB.split("/")[2]

_config = Config()

