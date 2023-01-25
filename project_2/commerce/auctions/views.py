from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Category, Listing, Comment, Bid


def index(request):
    activeListings = Listing.objects.filter(is_active=True)
    categories = Category.objects.all()
    return render(request, "auctions/index.html", {
        "listings": activeListings,
        "categories": categories,
    })


def displayCategory(request):
    if request.method == "POST":
        categoryForm = request.POST["category"]
        category = Category.objects.get(category_name=categoryForm)
        activeListings = Listing.objects.filter(is_active=True, category=category)
        categories = Category.objects.all()
        return render(request, "auctions/index.html", {
            "listings": activeListings,
            "categories": categories,
        })


def createListing(request):
    if request.method == "GET":
        categories = Category.objects.all()
        return render(request, "auctions/create.html", {
            "categories": categories,
        })
    
    # request.method == "POST"
    else:
        # get data from form
        title = request.POST["title"]
        description = request.POST["description"]
        imageUrl = request.POST["imageurl"]
        price = request.POST["price"]
        categoryForm = request.POST["category"]
        # set current user
        currentUser = request.user
        # get category data
        category = Category.objects.get(category_name=categoryForm)
        # create a Bid object
        bid = Bid(
            bid=int(price),
            user=currentUser,
        )
        bid.save()
        # create new Listing object
        newListing = Listing(
            title=title,
            description=description,
            image_url=imageUrl,
            price=bid,
            category=category,
            owner=currentUser,
        )
        # insert new listing to DB
        newListing.save()

        # redirect to index page
        return HttpResponseRedirect(reverse(index))


def listing(request, id):
    listingData = Listing.objects.get(pk=id)
    isListingInWatchlist = request.user in listingData.watchlist.all()
    allComments = Comment.objects.filter(listing=listingData)
    isOwner = request.user.username == listingData.owner.username
    return render(request, "auctions/listing.html", {
        "listing": listingData,
        "isListingInWatchlist": isListingInWatchlist,
        "allComments": allComments,
        "isOwner": isOwner,
    })


def displayWatchlist(request):
    currentUser = request.user
    listings = currentUser.watchlist.all()
    return render(request, "auctions/watchlist.html", {
        "listings": listings,
    })


def addWatchlist(request, id):
    listingData = Listing.objects.get(pk=id)
    currentUser = request.user
    listingData.watchlist.add(currentUser)
    return HttpResponseRedirect(reverse("listing", args=(id, )))


def removeWatchlist(request, id):
    listingData = Listing.objects.get(pk=id)
    currentUser = request.user
    listingData.watchlist.remove(currentUser)
    return HttpResponseRedirect(reverse("listing", args=(id, )))


def addComment(request, id):
    currentUser = request.user
    listingData = Listing.objects.get(pk=id)
    message = request.POST["newComment"]

    newComment = Comment(
        author = currentUser,
        listing = listingData,
        message = message,
    )
    newComment.save()

    return HttpResponseRedirect(reverse("listing", args=(id, )))


def addBid(request, id):
    if request.method == "POST":
        newBid = request.POST["newBid"]
        listingData = Listing.objects.get(pk=id)
        isListingInWatchlist = request.user in listingData.watchlist.all()
        allComments = Comment.objects.filter(listing=listingData)
        isOwner = request.user.username == listingData.owner.username

        if int(newBid) > listingData.price.bid:
            updateBid = Bid(user=request.user, bid=int(newBid))
            updateBid.save()
            listingData.price = updateBid
            listingData.save()
            return render(request, "auctions/listing.html", {
                "listing": listingData,
                "message": "Bid update success",
                "updated": True,
                "isListingInWatchlist": isListingInWatchlist,
                "allComments": allComments,
                "isOwner": isOwner,
            })
        else:
            return render(request, "auctions/listing.html", {
                "listing": listingData,
                "message": "Bid update fail",
                "updated": False,
                "isListingInWatchlist": isListingInWatchlist,
                "allComments": allComments,
                "isOwner": isOwner,
            })


def closeAuction(request, id):
    listingData = Listing.objects.get(pk=id)
    listingData.is_active = False
    listingData.save()
    isOwner = request.user.username == listingData.owner.username
    isListingInWatchlist = request.user in listingData.watchlist.all()
    allComments = Comment.objects.filter(listing=listingData)
    return render(request, "auctions/listing.html", {
        "listing": listingData,
        "isListingInWatchlist": isListingInWatchlist,
        "allComments": allComments,
        "isOwner": isOwner,
        "message": "Congratulation! Your auction is closed.",
        "updated": True,
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
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


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
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
