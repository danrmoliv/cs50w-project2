from django.contrib.auth.models import AbstractUser
from django.db import models
import datetime


class User(AbstractUser):
    pass

class Listing(models.Model):
    title = models.CharField(max_length=64, blank=False)
    description = models.CharField(max_length=5000, blank=False)
    min_price = models.FloatField(blank=False)
    image_url = models.CharField(max_length=500, blank=True)
    category = models.CharField(max_length=64, blank=True)
    listed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings')
    created_at = models.DateTimeField(auto_now_add=True) 
    highest_bid = models.FloatField(blank=True)
    highest_bid_user = models.ForeignKey(User, blank=True, on_delete=models.CASCADE, related_name='listing_highest_products', null=True)
    watched_by = models.ManyToManyField(User, blank=True, related_name="watchlist")
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} - Price: {self.min_price} - Listed by: {self.listed_by}"
    
class Bid(models.Model):
    product = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids_on_product")
    bid_value = models.FloatField(blank=False)
    user_bid = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bids_by_user')
    submited_at = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return f"{self.product} - Bid: {self.bid_value} - Bid from: {self.user_bid}"

class Comment(models.Model):
    product = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    comment = models.CharField(max_length=5000, blank=False)
    user_comment = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments_by_user')

    def __str__(self):
        return f"{self.product} - {self.comment}"