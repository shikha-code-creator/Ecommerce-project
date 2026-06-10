from django.db import models
from django.contrib.auth.models import User

class Customer(models.Model):
    cstnam=models.CharField(max_length=250,null=True)
    phone=models.CharField(max_length=250,null=True,unique=True)
    user=models.OneToOneField(User,on_delete=models.CASCADE,null=True)
    def __str__(self):
        return self.cstnam

class Product(models.Model):
    prdnam=models.CharField(max_length=250)
    description=models.TextField()
    price=models.FloatField()
    image=models.ImageField(upload_to="store/")
    def __str__(self):
        return self.prdnam

class Order(models.Model):
    customer=models.ForeignKey(Customer,on_delete=models.CASCADE)
    date_created=models.DateTimeField(auto_now_add=True)
    complete=models.BooleanField(default=False)
    transaction_id=models.CharField(max_length=500,null=True)
    @property
    def gettotqty(self):
        tot=sum([itm.quantity for itm in self.orderitems_set.all()])
        return tot

    @property
    def gettotbil(self):
        totbil=sum([itm.getlinetot for itm in self.orderitems_set.all()])
        return totbil

class OrderItems(models.Model):
    order=models.ForeignKey(Order,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity=models.IntegerField(default=0)
    @property
    def getlinetot(self):
        return self.product.price * self.quantity

class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    city = models.CharField(max_length=500)
    state = models.CharField(max_length=500)
    address= models.CharField(max_length=500)
    zipcode = models.CharField(max_length=50)
    def __str__(self):
        return self.address


