from django.contrib import admin
from .models import *
# Register your models here.


admin.site.register(VendorProfile)
admin.site.register(PurchaseOrder) 
admin.site.register(HistoricalPerformance)