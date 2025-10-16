from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse

from django.forms import ModelForm, ValidationError, Textarea
from .models import User, Listing, Bid, Comment

class ListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'description', 'min_price', 'image_url', 'category']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

class BidForm(ModelForm):
    class Meta:
        model = Bid
        fields = ['bid_value']
        labels = {
            'bid_value': '', 
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.min_price = kwargs.pop('min_price', 0)

        super().__init__(*args, **kwargs)        
    
        self.fields['bid_value'].widget.attrs['min'] = round(self.min_price, 2)

    def clean_price(self):
        bid = self.cleaned_data['bid_value']
        if bid <= self.min_price:
            raise ValidationError(f"Bid cannot be less than {self.min_price:2f}")
        return bid

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['comment']
        widgets = {
            'comment': Textarea(attrs={'rows': 4}),
        }
        labels = {
            'comment': '', 
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)



def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.all()
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("auctions:index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("auctions:index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("auctions:index"))
    else:
        return render(request, "auctions/register.html")

def listing_view(request, listing_id):
    
    listing = Listing.objects.get(id=listing_id)

    bid_text_info = False
    user_owner_listing = False

    if listing.listed_by == request.user:
        user_owner_listing = True
    
    print(user_owner_listing)

    total_bids = len(listing.bids_on_product.all())

    if (listing.is_available == False) and (request.user == listing.highest_bid_user):
        bid_text_info = f"You won the auction with your bid of $ {listing.highest_bid}."

    elif (total_bids > 0) and (request.user == listing.highest_bid_user):
        bid_text_info = f"{total_bids} bids so far. Your bid is the current bid."
        #print(bid_text_info) 
    elif total_bids > 0:
        bid_text_info = f"{total_bids} bids so far."
        #print(bid_text_info) 


    if float(listing.highest_bid) > float(listing.min_price):
        min_value_bid = float(listing.highest_bid) + 0.01
    else:
        min_value_bid = float(listing.min_price) - 0.000001

    form_bid = BidForm(user=request.user, min_price=min_value_bid)
    comment_form = CommentForm(user=request.user)

    user = request.user
    watched_by_user = False

    if user in listing.watched_by.all():
        watched_by_user = True

    return render(request, "auctions/listings.html", {
        "listing": listing,
        'form_bid': form_bid,
        'watched_by_user': watched_by_user,
        'bid_text_info': bid_text_info,
        'user_owner_listing': user_owner_listing,
        'comment_form': comment_form,
        "comments": listing.comments.all()
    })

def place_bid(request, listing_id):
    listing = Listing.objects.get(id=listing_id)

    if float(listing.highest_bid) > float(listing.min_price):
        min_value_bid = float(listing.highest_bid) + 0.01
    else:
        min_value_bid = float(listing.min_price) - 0.000001

    form_bid = BidForm(user=request.user, min_price=min_value_bid)

    if request.method == 'POST':
        print('request.method == POST - Make BID')

        form_bid = BidForm(request.POST, user=request.user)

        if form_bid.is_valid():
            new_bid = Bid(product = listing,
                          bid_value = form_bid.cleaned_data['bid_value'],
                          user_bid = form_bid.user)
            print(new_bid)
            print(form_bid.cleaned_data['bid_value'])

            print("Saving Bid")
            new_bid.save()

            listing.highest_bid = new_bid.bid_value
            listing.highest_bid_user = new_bid.user_bid
            listing.save()

            print(listing)
    
    return HttpResponseRedirect(reverse("auctions:listing", kwargs={"listing_id": listing.id}))



def listing_new(request):
    
    if request.method == 'POST':

        form = ListingForm(request.POST, user=request.user)

        if form.is_valid():

            new_listing = Listing(title=form.cleaned_data['title'], 
                    description=form.cleaned_data['description'],
                    min_price = form.cleaned_data['min_price'],
                    image_url = form.cleaned_data['image_url'],
                    category = form.cleaned_data['category'],
                    listed_by = form.user,
                    highest_bid = 0
                    )

            new_listing.save()

            form_bid = BidForm(user=request.user)

        return HttpResponseRedirect(reverse("auctions:listing", kwargs={"listing_id": new_listing.id}))

    else:
        form = ListingForm(user=request.user)
        return render(request, "auctions/add_listing.html", {
            "form": form
        })

def add_to_watchlist(request, listing_id):

    if request.method == 'POST':

        listing = Listing.objects.get(id=listing_id)

        user = request.user

        listing.watched_by.add(user)

        return HttpResponseRedirect(reverse("auctions:listing", kwargs={"listing_id": listing.id}))
    
def watchlist(request):
    user = request.user

    #listings = Listing.objects.all()

    listing_watch = Listing.objects.filter(watched_by = user).all()

    return render(request, "auctions/watchlist.html", {
        "listings": listing_watch
    })

def remove_from_watchlist(request, listing_id):

    if request.method == 'POST':

        listing = Listing.objects.get(id=listing_id)

        user = request.user

        listing.watched_by.remove(user)

        return HttpResponseRedirect(reverse("auctions:listing", kwargs={"listing_id": listing.id}))
    

def close_auction(request, listing_id):

    if request.method == 'POST':

        listing = Listing.objects.get(id=listing_id)
        listing.is_available = False

        listing.save()

        return HttpResponseRedirect(reverse("auctions:listing", kwargs={"listing_id": listing.id}))
 
 
def add_comment(request, listing_id):

    if request.method == 'POST':

        listing = Listing.objects.get(id=listing_id)
        
        comment_form = CommentForm(request.POST, user=request.user)

        if comment_form.is_valid():
            new_comment = Comment(product = listing,
                          comment = comment_form.cleaned_data['comment'],
                          user_comment = comment_form.user)
            new_comment.save()

        return HttpResponseRedirect(reverse("auctions:listing", kwargs={"listing_id": listing.id}))
 