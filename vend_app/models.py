from django.db import models
from django.db.models import Avg


class VendorProfile(models.Model):
    name = models.CharField(max_length=100)
    contact_details = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    vendor_code = models.CharField(max_length=20, unique=True)
    on_time_delivery_rate = models.FloatField()
    quality_rating_avg = models.FloatField()
    average_response_time = models.FloatField()
    fulfillment_rate = models.FloatField()

    def update_quality_rating_avg(self):
        completed_pos = PurchaseOrder.objects.filter(vendor_reference=self, status='True', quality_rating__isnull=False)
        avg_rating = completed_pos.aggregate(avg_quality_rating=Avg('quality_rating'))['avg_quality_rating'] or 0
        self.quality_rating_avg = avg_rating
        self.save()

    def update_average_response_time(self):
        response_times = PurchaseOrder.objects.filter(vendor_reference=self, acknowledgment_date__isnull=False).annotate(
            response_time=models.F('acknowledgment_date') - models.F('issue_date')
        ).aggregate(avg_response_time=Avg('response_time'))['avg_response_time']
        if response_times:
            self.average_response_time = response_times.total_seconds() / 60  # Convert to minutes
            self.save()

    def update_fulfillment_rate(self):
        total_pos = PurchaseOrder.objects.filter(vendor_reference=self).count()
        if total_pos == 0:
            self.fulfillment_rate = 0
        else:
            completed_pos = PurchaseOrder.objects.filter(vendor_reference=self, status=True).count()
            self.fulfillment_rate = (completed_pos / total_pos) * 100
        self.save()

    def __str__(self):
        return self.name


class PurchaseOrder(models.Model):
    po_number = models.CharField(max_length=100, unique=True)
    vendor_reference = models.ForeignKey(VendorProfile, on_delete=models.CASCADE)
    order_date = models.DateField()
    ITEMS_CHOICES = [
        ('Item1', 'Item1'),
        ('Item2', 'Item2'),
        ('Item3', 'Item3'),
        # Add more choices as needed
    ]
    items = models.CharField(max_length=50, choices=ITEMS_CHOICES)
    quantity = models.PositiveIntegerField()
    STATUS_CHOICES = [
        ('pending', 'pending'),
        ('completed', 'completed'),
        ('canceled', 'canceled')
    ]
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default=True)
    delivery_date = models.DateField()
    quality_rating = models.FloatField(null=True)  # Nullable field
    issue_date = models.DateTimeField()  # Timestamp when the PO was issued to the vendor
    acknowledgment_date = models.DateTimeField(null=True) 

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.status and self.quality_rating is not None:
            self.vendor_reference.update_quality_rating_avg()

    def purchase_save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.status and self.acknowledgment_date:
            self.vendor_reference.update_average_response_time()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.vendor_reference.update_fulfillment_rate()

    def __str__(self):
        return self.po_number


class HistoricalPerformance(models.Model):
    vendor = models.ForeignKey(VendorProfile, on_delete=models.CASCADE)
    date = models.DateTimeField()
    on_time_delivery_rate = models.FloatField()
    quality_rating_avg = models.FloatField()
    average_response_time = models.FloatField()
    fulfillment_rate = models.FloatField()

    def __str__(self):
        return f"{self.vendor.name} - {self.date}"