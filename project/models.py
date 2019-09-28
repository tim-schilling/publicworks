from django.db import models


class Address(models.Model):
    street_number = models.CharField(max_length=16)
    street_direction = models.CharField(max_length=16, null=False, default='', blank=True)
    street_name = models.CharField(max_length=100)
    street_type = models.CharField(max_length=16, null=False, default='', blank=True)
    street_suffix = models.CharField(max_length=16, null=False, default='', blank=True)
    zipcode = models.CharField(max_length=5, null=False, default='', blank=True)
    street2 = models.CharField(max_length=256, null=False, default='', blank=True)
    other = models.CharField(max_length=256, null=False, default='', blank=True)
    primary_residence = models.BooleanField(default=False)

    def format(self):
        values = [
            self.street_number,
            self.street_direction,
            self.street_name,
            self.street_type,
            self.street_suffix,
            self.zipcode,
            self.street2,
            self.other,
        ]
        return ' '.join([s for s in values if s])


class PublicWorksAttributeMixin(models.Model):
    class Meta:
        abstract = True
    code = models.CharField(max_length=16)
    text = models.CharField(max_length=256)

    def __str__(self):
        return f'{self.code}: {self.text}'

class Category(PublicWorksAttributeMixin):
    pass


class Problem(PublicWorksAttributeMixin):
    pass


class Department(PublicWorksAttributeMixin):
    pass


class Route(PublicWorksAttributeMixin):
    pass


class TimeCost(PublicWorksAttributeMixin):
    pass


class Cause(PublicWorksAttributeMixin):
    pass


class Task(PublicWorksAttributeMixin):
    pass


class Crew(PublicWorksAttributeMixin):
    pass


class Unit(PublicWorksAttributeMixin):
    pass


class WorkRequestStatus(PublicWorksAttributeMixin):
    updated = models.DateTimeField()


class Division(PublicWorksAttributeMixin):
    related_asset = models.CharField(max_length=64, blank=True)


class Facility(PublicWorksAttributeMixin):
    address = models.ForeignKey(Address, null=True, blank=True)


class Location(PublicWorksAttributeMixin):
    address = models.ForeignKey(Address, null=True, blank=True)


class WorkOrderStatus(PublicWorksAttributeMixin):
    updated = models.DateTimeField()


class ResourceType(PublicWorksAttributeMixin):
    pass


class Resource(PublicWorksAttributeMixin):
    type = models.ForeignKey(ResourceType)
    default_unit_cost = models.DecimalField()


class Asset(models.Model):
    code = models.CharField(max_length=64)
    desc1 = models.CharField(max_length=256, blank=True)
    desc2 = models.CharField(max_length=256, blank=True)


class Project(models.Model):
    code = models.CharField(max_length=64)


class WorkRequest(models.Model):
    project = models.OneToOneField(Project, related_name='work_request', on_delete=models.CASCADE)
    received = models.DateTimeField()
    priority = models.IntegerField(null=True, blank=True)
    status = models.ForeignKey(WorkRequestStatus, related_name='work_requests', on_delete=models.CASCADE)
    category = models.ForeignKey(Category, related_name='work_requests', on_delete=models.CASCADE, null=True, blank=True)
    problem = models.ForeignKey(Problem, related_name='work_requests', on_delete=models.CASCADE, null=True, blank=True)
    department = models.ForeignKey(Department, related_name='work_requests', on_delete=models.CASCADE, null=True, blank=True)
    division = models.ForeignKey(Division, related_name='work_requests', on_delete=models.CASCADE, null=True, blank=True)
    after_hours = models.BooleanField()
    callback_requested = models.NullBooleanField()
    projected_start = models.DateField(null=True, blank=True)
    facility = models.ForeignKey(Facility, related_name='work_requests', on_delete=models.CASCADE, null=True, blank=True)
    location = models.ForeignKey(Location, related_name='work_requests', on_delete=models.CASCADE, null=True, blank=True)
    address = models.ForeignKey(Address, related_name='work_requests', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f'<WorkRequest project={self.project.code!r}>'


class WorkOrder(models.Model):
    project = models.ForeignKey(Project, related_name='work_orders', on_delete=models.CASCADE)
    status = models.ForeignKey(WorkOrderStatus, related_name='work_orders', on_delete=models.CASCADE)
    created = models.DateField()
    category = models.ForeignKey(Category, related_name='work_orders', on_delete=models.CASCADE)
    department = models.ForeignKey(Department, related_name='work_orders', on_delete=models.CASCADE, null=True, blank=True)
    division = models.ForeignKey(Division, related_name='work_orders', on_delete=models.CASCADE, null=True, blank=True)
    priority = models.IntegerField(null=True, blank=True)
    total_cost = models.DecimalField()
    quantity = models.IntegerField()
    labor_hours = models.DecimalField()
    labor_cost = models.DecimalField()
    equipment_cost = models.DecimalField()
    material_cost = models.DecimalField()
    contractor_cost = models.DecimalField()
    misc_cost = models.DecimalField()
    start = models.DateField(null=True, blank=True)
    end = models.DateField(null=True, blank=True)
    duration = models.IntegerField()
    billing_required = models.BooleanField()
    task = models.ForeignKey(Task, related_name='work_orders', on_delete=models.CASCADE, null=True, blank=True)
    cause = models.ForeignKey(Cause, related_name='work_orders', on_delete=models.CASCADE, null=True, blank=True)
    problem = models.ForeignKey(Problem, related_name='work_orders', on_delete=models.CASCADE, null=True, blank=True)
    asset = models.ForeignKey(Asset, related_name='work_orders', on_delete=models.CASCADE, null=True, blank=True)
    assigned_crew = models.ForeignKey(Crew, related_name='work_orders', on_delete=models.CASCADE, null=True, blank=True)
    supervisor = models.IntegerField(null=True, blank=True)
    lead_worker = models.IntegerField(null=True, blank=True)
    address = models.ForeignKey(Address, related_name='work_orders', on_delete=models.CASCADE, null=True, blank=True)
    facility = models.ForeignKey(Facility, related_name='work_orders', on_delete=models.CASCADE, null=True, blank=True)
    project_number = models.CharField(max_length=64, blank=True)
    Route = models.ForeignKey(Route, related_name='work_orders', on_delete=models.CASCADE, null=True, blank=True)


class WorkDetail(models.Model):
    created = models.DateField()
    start = models.DateField()
    end = models.DateField()
    duration = models.IntegerField()
    updated = models.DateField(null=True, blank=True)
    task = models.ForeignKey(Task, related_name='work_details', on_delete=models.CASCADE, null=True, blank=True)
    resource = models.ForeignKey(Resource, related_name='work_details', on_delete=models.CASCADE, null=True, blank=True)
    resource_desc = models.CharField(max_length=256, blank=True)
    unit_cost = models.DecimalField(null=True, blank=True)
    units = models.DecimalField(null=True, blank=True)
    total_cost = models.DecimalField(null=True, blank=True)
    total_units = models.DecimalField(null=True, blank=True)
    unit_cost_regular_time = models.DecimalField(null=True, blank=True)
    unit_cost_overtime = models.DecimalField(null=True, blank=True)
    overtime_unit_cost = models.DecimalField(null=True, blank=True)
    grand_total_cost = models.DecimalField(null=True, blank=True)
    time_cost = models.ForeignKey(TimeCost, related_name='work_details', on_delete=models.CASCADE, null=True, blank=True)
    unit = models.ForeignKey(Unit, related_name='work_details', on_delete=models.CASCADE, null=True, blank=True)
