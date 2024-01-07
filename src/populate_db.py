import csv
from database.models import MailingTarget

targets = list()
with open("data.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f, delimiter=",")
    for line in reader:
        if line["first_name"] == r"\N":
            line["first_name"] = None
        line["done_at"] = None
        line["worker"] = None
        line["status"] = "PENDING"
        targets.append(MailingTarget(**line))
from database import Session

session = Session()
session.add_all(targets)
session.commit()
print(targets)
