import csv
from datetime import datetime
from django.db.models import Count
import pytz
from . import models

TZ = pytz.timezone("America/Chicago")

REQUEST_ATTRIBUTES = [
    ("Status", "Status Text", models.WorkRequestStatus, "status"),
    ("Category", "Category Text", models.Category, "category"),
    ("Problem", "Problem Text", models.Problem, "problem"),
    ("Department", "Department Text", models.Department, "department"),
    ("Division", "Division Text", models.Division, "division"),
    ("Facility Building", "Facility Building Text", models.Facility, "facility"),
    ("Location", "Location Text", models.Location, "location"),
    # Address
]

ORDER_ATTRIBUTES = [
    ("Status", "Status Text", models.WorkOrderStatus, "status"),
    ("Category Code", "Category Text", models.Category, "category"),
    ("Problem", "Problem Text", models.Problem, "problem"),
    ("Department", "Department Text", models.Department, "department"),
    ("Division", "Division Text", models.Division, "division"),
    ("Main Task", "Main Task Text", models.Task, "task"),
    ("Assigned Crew", "Assigned Crew Text", models.Crew, "assigned_crew"),
    ("Route (Geographic)", "Route (Geographic) Text", models.Route, "route"),
    ("Cause", "Cause Text", models.Cause, "cause"),
    # Asset
    # Address
    # Facility Location
]

DETAIL_ATTRIBUTES = [
    ("Task Code", "Task Text", models.Task, "task"),
    ("Resource Type", "Resource Type Text", models.ResourceType, None),
    # ('Resource', 'Resource Text'),
    ("Time Cost", "Time Cost Text", models.TimeCost, "time_cost"),
    ("Unit of Measure", "Unit of Measure Text", models.Unit, "unit"),
]


def clean_attribute_duplicates():
    models = (
        [a[2] for a in REQUEST_ATTRIBUTES]
        + [a[2] for a in ORDER_ATTRIBUTES]
        + [a[2] for a in DETAIL_ATTRIBUTES]
    )
    for m in models:
        for code in (
            m.objects.values("code")
            .annotate(count=Count("code"))
            .filter(count__gt=1)
            .values_list("code", flat=True)
        ):
            value = ""
            for text in m.objects.filter(code=code).values_list("text", flat=True):
                if len(text) > len(value):
                    value = text
            final = m.objects.filter(code=code).first()
            final.text = value
            final.save()
            m.objects.filter(code=code).exclude(id=final.id).delete()
        m.objects.filter(code="").delete()
        m.objects.filter(code=" ").delete()


def clean_attribute(dict_reader, code_field, text_field):
    results = set()
    try:
        for row in dict_reader:
            if not row[code_field]:
                continue
            results.add((row[code_field], row[text_field]))
    except KeyError:
        return None
    return results


def populate_attribute_models(filepath, attributes):
    with open(filepath, mode="r") as f:
        dict_reader = csv.DictReader(f)
        for attr_code, attr_text, model, _ in attributes:
            f.seek(1)
            data = clean_attribute(dict_reader, attr_code, attr_text)
            if not data:
                continue
            for code, text in data:
                instance = model.objects.filter(code=code).first()
                if not instance:
                    model.objects.create(code=code, text=text)
                elif len(instance.text) < len(text):
                    instance.text = text
                    instance.save()


ADDRESS_MAP = {
    "Street Address": "street_number",
    "Street Number": "street_number",
    "Street Direction": "street_direction",
    "Street Name": "street_name",
    "Street Type": "street_type",
    "Street Suffix": "street_suffix",
    "Loc Zip Code": "zipcode",
    "Other Location Information": "other",
}


def parse_address(row):
    attributes = {
        "other": row.get("Other Location Information") == "True",
        "street2": " ".join(
            [
                s
                for s in [
                    row.get("Street 2 Direction"),
                    row.get("Street 2 Name"),
                    row.get("Street 2 Type"),
                ]
                if s
            ]
        ),
        "street_number": row.get("Street Address") or row.get("Street Number") or "",
    }
    for csv_key, model_key in ADDRESS_MAP.items():
        attributes[model_key] = row.get(csv_key) or ""
    address = models.Address.objects.filter(**attributes).first()
    if not address:
        address = models.Address.objects.create(**attributes)
    return address


def parse_project(row, field):
    code = row[field]
    project, _ = models.Project.objects.get_or_create(code=code)
    return project


def parse_datetime(date_str, time_str):
    try:
        d = datetime.strptime(date_str, "%m/%d/%Y %H:%M:%S")
    except ValueError:
        d = datetime.strptime(date_str, "%m/%d/%Y %H:%M")
    try:
        t = datetime.strptime(time_str, "%m/%d/%Y %H:%M:%S")
    except ValueError:
        t = datetime.strptime(time_str, "%m/%d/%Y %H:%M")
    return TZ.localize(datetime.combine(d.date(), t.time()))


def parse_date(date_str):
    if not date_str:
        return None
    try:
        d = datetime.strptime(date_str, "%m/%d/%Y %H:%M:%S").date()
    except ValueError:
        try:
            d = datetime.strptime(date_str, "%m/%d/%Y %H:%M").date()
        except ValueError:
            d = datetime.strptime(date_str, "%m/%d/%Y").date()
    return d


def process_requests():
    populate_attribute_models("data/work_request.csv", REQUEST_ATTRIBUTES)
    with open("data/work_request.csv", mode="r") as f:
        dict_reader = csv.DictReader(f)
        for r in dict_reader:
            address = parse_address(r)
            project = parse_project(r, "Requisition Number")
            attributes = {
                "received": parse_datetime(r["Received Date"], r["Received Time"]),
                "priority": r.get("priority") and int(r["priority"]),
                "updated": parse_date(r["Status Date"]),
                "projected_start": parse_date(r["Projected Start Date"]),
                "after_hours": r["After Hours"] == "TRUE",
                "callback_requested": r.get("Call Back Requested")
                and r["Call Back Requested"] == "TRUE",
                "address": address,
                "related_asset": r["Related Asset Type"],
            }
            for key, _, model, model_field in REQUEST_ATTRIBUTES:
                attributes[model_field] = model.objects.filter(code=r[key]).first()
            models.WorkRequest.objects.update_or_create(
                project=project, defaults=attributes
            )


def parse_asset(row):
    return models.Asset.objects.get_or_create(
        code=row["Asset"] or "", desc1=row["Desc 1"] or "", desc2=row["Desc 2"] or ""
    )[0]


def parse_facility(row):
    value = row["Facility Location"]
    if not value:
        return None
    try:
        return models.Facility.objects.get(text=value)
    except models.Facility.DoesNotExist:
        return models.Facility.objects.create(code=value, text=value)


def process_orders():
    populate_attribute_models("data/work_order_summary.csv", ORDER_ATTRIBUTES)
    with open("data/work_order_summary.csv", mode="r") as f:
        dict_reader = csv.DictReader(f)
        for r in dict_reader:
            address = parse_address(r)
            project = parse_project(r, "Work Order Number")
            attributes = {
                "created": parse_date(r["Creation Date"]),
                "priority": (r.get("priority") or None) and int(r["priority"]),
                "updated": parse_date(r["Status Date"]),
                "total_cost": r["Total Cost"],
                "quantity": r["Quantity"],
                "labor_hours": r["Actual Labor Hours"],
                "labor_cost": r["Actual Labor Cost"],
                "equipment_cost": r["Actual Equip Cost"],
                "material_cost": r["Actual Material Cost"],
                "contractor_cost": r["Contractor Cost"],
                "misc_cost": r["Misc. Cost"],
                "duration": r["Duration Actual(Hrs)"],
                "billing_required": r["Billing Required"] == "TRUE",
                "supervisor": r["Supervisor"] or None,
                "lead_worker": r["LeadWorker Id"] or None,
                "project_number": r["Project Number"],
                "address": address,
                "facility": parse_facility(r),
                "asset": parse_asset(r),
            }
            for key, _, model, model_field in ORDER_ATTRIBUTES:
                attributes[model_field] = model.objects.filter(code=r[key]).first()
            models.WorkOrder.objects.update_or_create(
                project=project, defaults=attributes
            )


def parse_resource(row):
    if not row["Resource"]:
        return None
    type = models.ResourceType.objects.get(code=row["Resource Type"])
    resource, _ = models.Resource.objects.get_or_create(
        code=row["Resource"],
        type=type,
        defaults={
            "default_unit_cost": row["Default Unit Cost"],
            "text": row["Resource Text"],
        },
    )
    return resource


def process_details():
    populate_attribute_models("data/work_order_detail.csv", DETAIL_ATTRIBUTES)
    with open("data/work_order_detail.csv", mode="r") as f:
        dict_reader = csv.DictReader(f)
        for r in dict_reader:
            project = parse_project(r, "Work Order Number")
            attributes = {
                "created": parse_date(r["Creation Date"]),
                "start": parse_date(r["Start Date"]),
                "end": parse_date(r["End Date"]),
                "duration": r["Duration Actual(Hrs)"],
                "updated": parse_date(r["Status Date"]),
                "resource_desc": r["Additional Description"],
                "unit_cost": r["Unit Cost"] or None,
                "units": r["Units"] or None,
                "total_cost": r["Total Cost"] or None,
                "total_units": r["Grand Total Units"] or None,
                "unit_cost_regular_time": r["Unit Cost-Regular Time"] or None,
                "unit_cost_overtime": r["Unit Cost-Overtime"] or None,
                "overtime_unit_cost": r["Override Unit Cost"] or None,
                "grand_total_cost": r["Grand Total Cost"] or None,
                "resource": parse_resource(r),
            }
            for key, _, model, model_field in DETAIL_ATTRIBUTES:
                if not model_field:
                    continue
                attributes[model_field] = model.objects.filter(code=r[key]).first()
            models.WorkDetail.objects.update_or_create(
                project=project, defaults=attributes
            )
