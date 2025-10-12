from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from django.forms import ModelForm
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

    form_bid = BidForm(user=request.user)

    return render(request, "auctions/listings.html", {
        "listing": listing,
        'form_bid': form_bid
    })

def listing_new(request):
    
    if request.method == 'POST':
        print('request.method == POST')

        form = ListingForm(request.POST, user=request.user)

        if form.is_valid():

            new_listing = Listing(title=form.cleaned_data['title'], 
                    description=form.cleaned_data['description'],
                    min_price = form.cleaned_data['min_price'],
                    image_url = form.cleaned_data['image_url'],
                    category = form.cleaned_data['category'],
                    listed_by = form.user
                    )

            new_listing.save()



    form = ListingForm(user=request.user)
    return render(request, "auctions/add_listing.html", {
        "form": form
    })


# def listing_add(request):

#     if request.method == 'POST':

#         form = ListingForm(request.POST)

#         if form.is_valid():


#     form = ListingForm()
#     return render(request, "auctions/add_listing.html", {
#         "form": form
#     })