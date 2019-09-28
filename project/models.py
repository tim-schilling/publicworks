from django.db import models


class Address(models.Model):
    street_number = models.CharField(max_length=16)
    street_direction = models.CharField(
        max_length=16, null=False, default="", blank=True
    )
    street_name = models.CharField(max_length=100)
    street_type = models.CharField(max_length=16, null=False, default="", blank=True)
    street_suffix = models.CharField(max_length=16, null=False, default="", blank=True)
    zipcode = models.CharField(max_length=5, null=False, default="", blank=True)
    street2 = models.CharField(max_length=256, null=False, default="", blank=True)
    other = models.CharField(max_length=256, null=False, default="", blank=True)
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
        return " ".join([s for s in values if s])


class PublicWorksAttributeMixin(models.Model):
    class Meta:
        abstract = True

    code = models.CharField(max_length=64, unique=True)
    text = models.CharField(max_length=256)

    def __str__(self):
        return f"{self.code}: {self.text}"


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
    pass


class Division(PublicWorksAttributeMixin):
    pass


class Facility(PublicWorksAttributeMixin):
    address = models.ForeignKey(
        Address, null=True, blank=True, on_delete=models.CASCADE
    )


class Location(PublicWorksAttributeMixin):
    address = models.ForeignKey(
        Address, null=True, blank=True, on_delete=models.CASCADE
    )


class WorkOrderStatus(PublicWorksAttributeMixin):
    pass


class ResourceType(PublicWorksAttributeMixin):
    pass


class Resource(models.Model):
    class Meta:
        unique_together = [("code", "type")]

    code = models.CharField(max_length=64)
    text = models.CharField(max_length=256)
    type = models.ForeignKey(
        ResourceType, related_name="resources", on_delete=models.CASCADE
    )
    default_unit_cost = models.DecimalField(max_digits=12, decimal_places=4)


class Asset(models.Model):
    code = models.CharField(max_length=64)
    desc1 = models.CharField(max_length=256, blank=True)
    desc2 = models.CharField(max_length=256, blank=True)


class Project(models.Model):
    code = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.code


class WorkRequest(models.Model):
    project = models.OneToOneField(
        Project, related_name="work_request", on_delete=models.CASCADE
    )
    received = models.DateTimeField()
    priority = models.IntegerField(null=True, blank=True)
    status = models.ForeignKey(
        WorkRequestStatus, related_name="work_requests", on_delete=models.CASCADE
    )
    updated = models.DateField()
    category = models.ForeignKey(
        Category,
        related_name="work_requests",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    problem = models.ForeignKey(
        Problem,
        related_name="work_requests",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    department = models.ForeignKey(
        Department,
        related_name="work_requests",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    division = models.ForeignKey(
        Division,
        related_name="work_requests",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    after_hours = models.BooleanField()
    callback_requested = models.NullBooleanField()
    projected_start = models.DateField(null=True, blank=True)
    facility = models.ForeignKey(
        Facility,
        related_name="work_requests",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    location = models.ForeignKey(
        Location,
        related_name="work_requests",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    address = models.ForeignKey(
        Address,
        related_name="work_requests",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    related_asset = models.CharField(max_length=64, blank=True)

    def __str__(self):
        return f"<WorkRequest project={self.project.code!r}>"


class WorkOrder(models.Model):
    project = models.ForeignKey(
        Project, related_name="work_orders", on_delete=models.CASCADE, unique=True
    )
    status = models.ForeignKey(
        WorkOrderStatus, related_name="work_orders", on_delete=models.CASCADE
    )
    created = models.DateField()
    updated = models.DateField()
    category = models.ForeignKey(
        Category, related_name="work_orders", on_delete=models.CASCADE
    )
    department = models.ForeignKey(
        Department,
        related_name="work_orders",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    division = models.ForeignKey(
        Division,
        related_name="work_orders",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    priority = models.IntegerField(null=True, blank=True)
    total_cost = models.DecimalField(max_digits=12, decimal_places=4)
    quantity = models.IntegerField()
    labor_hours = models.DecimalField(max_digits=12, decimal_places=4)
    labor_cost = models.DecimalField(max_digits=12, decimal_places=4)
    equipment_cost = models.DecimalField(max_digits=12, decimal_places=4)
    material_cost = models.DecimalField(max_digits=12, decimal_places=4)
    contractor_cost = models.DecimalField(max_digits=12, decimal_places=4)
    misc_cost = models.DecimalField(max_digits=12, decimal_places=4)
    start = models.DateField(null=True, blank=True)
    end = models.DateField(null=True, blank=True)
    duration = models.IntegerField()
    billing_required = models.BooleanField()
    task = models.ForeignKey(
        Task,
        related_name="work_orders",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    cause = models.ForeignKey(
        Cause,
        related_name="work_orders",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    problem = models.ForeignKey(
        Problem,
        related_name="work_orders",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    asset = models.ForeignKey(
        Asset,
        related_name="work_orders",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    assigned_crew = models.ForeignKey(
        Crew,
        related_name="work_orders",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    supervisor = models.IntegerField(null=True, blank=True)
    lead_worker = models.IntegerField(null=True, blank=True)
    address = models.ForeignKey(
        Address,
        related_name="work_orders",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    facility = models.ForeignKey(
        Facility,
        related_name="work_orders",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    project_number = models.CharField(max_length=64, blank=True)
    route = models.ForeignKey(
        Route,
        related_name="work_orders",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )


class WorkDetail(models.Model):
    project = models.ForeignKey(
        Project, related_name="work_details", on_delete=models.CASCADE
    )
    created = models.DateField()
    start = models.DateField(null=True, blank=True)
    end = models.DateField(null=True, blank=True)
    duration = models.IntegerField()
    updated = models.DateField(null=True, blank=True)
    task = models.ForeignKey(
        Task,
        related_name="work_details",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    resource = models.ForeignKey(
        Resource,
        related_name="work_details",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    resource_desc = models.CharField(max_length=256, blank=True)
    unit_cost = models.DecimalField(
        null=True, blank=True, max_digits=12, decimal_places=4
    )
    units = models.DecimalField(null=True, blank=True, max_digits=12, decimal_places=4)
    total_cost = models.DecimalField(
        null=True, blank=True, max_digits=12, decimal_places=4
    )
    total_units = models.DecimalField(
        null=True, blank=True, max_digits=12, decimal_places=4
    )
    unit_cost_regular_time = models.DecimalField(
        null=True, blank=True, max_digits=12, decimal_places=4
    )
    unit_cost_overtime = models.DecimalField(
        null=True, blank=True, max_digits=12, decimal_places=4
    )
    overtime_unit_cost = models.DecimalField(
        null=True, blank=True, max_digits=12, decimal_places=4
    )
    grand_total_cost = models.DecimalField(
        null=True, blank=True, max_digits=12, decimal_places=4
    )
    time_cost = models.ForeignKey(
        TimeCost,
        related_name="work_details",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    unit = models.ForeignKey(
        Unit,
        related_name="work_details",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
