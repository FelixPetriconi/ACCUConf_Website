
from pathlib import Path


class ConfigBase:
    _here = Path(__file__).parent
    _database_path = _here / 'accuconf.db'
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + str(_database_path)
    DEBUG = False
    DATA_DIR = _here / 'etc' / 'data'
    VENUE = DATA_DIR / "venue.json"
    COMMITTEE = DATA_DIR / "committee.json"
    MAINTENANCE = False
    SECRET_KEY = "TheObviouslyOpenSecret"
    NIKOLA_STATIC_PATH = _here / 'accuconf' / 'static'


class ProductionConfig(ConfigBase):
    pass


class MaintenanceProductionConfig(ProductionConfig):
    MAINTENANCE = True


class TestConfig(ConfigBase):
    _database_path = ConfigBase._here / 'accuconf_test.db'
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + str(_database_path)
    DEBUG = True


class MaintenanceTestConfig(TestConfig):
    MAINTENANCE = True


# Config = ProductionConfig
# Config = MaintenanceProductionConfig
Config = TestConfig
# Config = MaintenanceTestConfig
