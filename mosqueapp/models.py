from django.db import models
from django.contrib.auth.models import User
import calendar
# Create your models here.
class AdminProfile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    ROLE_CHOICES=(
        ('super','Super Admin'),
        ('payment','Payment  Operator')
    )
    role=models.CharField(max_length=20,choices=ROLE_CHOICES)

class MonthlyAmountSetting(models.Model):
    amount = models.PositiveIntegerField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Monthly Amount: ₹{self.amount}"

class Member(models.Model):
    member_id=models.CharField(max_length=10,unique=True,null=False)
    member_name=models.CharField(max_length=255)
    member_phone=models.CharField(max_length=15,unique=True)
    member_email=models.EmailField(null=True,blank=True)
    address=models.TextField(max_length=500)
    payment_status=models.BooleanField(default=False)
    is_active=models.BooleanField(default=True)
    deleted = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        self.member_id = self.member_id.zfill(5)
        super().save(*args, **kwargs)

    
class MonthlyPayment(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    year = models.PositiveIntegerField()
    month = models.PositiveSmallIntegerField(choices=[(i, calendar.month_name[i]) for i in range(1, 13)])
    amount = models.PositiveIntegerField()
    paid = models.BooleanField(default=False)
    paid_on = models.DateField(null=True, blank=True,auto_now_add=True)

    class Meta:
        unique_together = ('member', 'year', 'month')
        ordering = ['-year', '-month']
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # After saving, update the member's overall payment status
        any_paid = MonthlyPayment.objects.filter(member=self.member, paid=True).exists()
        self.member.payment_status = any_paid
        self.member.save()

    def __str__(self):
        return f"{self.member.member_name} - {self.month}/{self.year} - {'Paid' if self.paid else 'Pending'}"
