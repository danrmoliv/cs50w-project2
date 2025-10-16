from django.urls import path

from . import views

app_name = 'auctions'

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("listings/<int:listing_id>", views.listing_view, name="listing"),
    path("listings/new", views.listing_new, name='new_listing'),
    path("listings/add_watchlist/<int:listing_id>", views.add_to_watchlist, name="add_to_watchlist"),
    path("listings/remove_watchlist/<int:listing_id>", views.remove_from_watchlist, name="remove_from_watchlist"),
    path("listings/place_bid/<int:listing_id>", views.place_bid, name="place_bid"),
    path("listings/close_auction/<int:listing_id>", views.close_auction, name="close_auction"),
    path("listings/add_comment/<int:listing_id>", views.add_comment, name="add_comment"),
    path("listings/watchlist", views.watchlist, name="watchlist"),
    path("listings/categories", views.categories, name="categories"),
    path("listings/categories/<str:category_name>", views.categories_items, name="categories_items")
]
