from django.shortcuts import render
from django.http import HttpResponse,Http404,HttpResponseRedirect
from .models import *
from django.shortcuts import get_object_or_404
from instamojo_wrapper import Instamojo
from home import API_KEY,AUTH_TOKEN
from django.urls import reverse
from datetime import datetime
api = Instamojo(api_key=API_KEY, auth_token=AUTH_TOKEN, endpoint='https://test.instamojo.com/api/1.1/')

# Create your views here.
def index(request):
    return HttpResponse("HomePage-OK")

def bookDetailView(request,bid):
    bk=get_object_or_404(Book,pk=bid)
    return HttpResponse(bk.title)

def catalogView(request):
    if request.method=="GET":
        pass
    else:
        books=Book.objects.all()
        p=""
        for i in books:
            p+="<p>"+book.title+"</p>"
        return HttpResponse(p)

def paymentView(request):
    bid=request.session.get("book_id",-1)    
    if(bid==-1):
        return Http404
    if request.method=="POST":
        topay=Book.objects.get(id=bid).mrp
        balance=request.user.profile.balance
        if 'usebal' in request.POST:
            if(balance>Book.objects.get(id=bid).mrp):
                topay=0
            else:
                topay-=balance
        if(topay>0):
            if(topay<10):
                topay=10
            response = api.payment_request_create(
                        amount=str(topay),
                        purpose="Rentafolio Book Rental",
                        send_email=False,
                        email=request.user.email,
                        buyer_name=request.user.username,
                        phone=request.user.profile.phone,
                        redirect_url=request.build_absolute_uri(reverse("checkout")),
                    )    
            return HttpResponseRedirect(response['payment_request']['longurl'])
        else:
            usr=request.user.profile
            usr.balance-=Book.objects.get(id=bid).mrp
            usr.save()
        book_instances=Book.bookinstance_set.all()
        for i in book_instances:
            if(i.status==1):
                i.borrower=request.user.profile
                i.b_date=datetime.now()
                i.status=0
                i.save()
                break
        request.session["book_issued",bid]
        return HttpResponseRedirect(reverse('checkout'))
    return HttpResponse("PaymentPage-OK")

        

def profileView(request):
    return HttpResponse("profileView-OK")

def issuedView(request):
    if request.method=="POST":
        return_id=int(request.POST['return_id'])
        return_book=BookInstance.objects.get(id=return_id)
        return_book.borrower=None
        return_book.status=1
        return_book.save()
        messages.warning(request,"Book successfully returned")
        return HttpResponse("OK")
    issued_books=request.user.profile.borrowed.all()
    p=""
    if len(issued_books==0):
        return HttpResponse("You dont have any books issued")
    else:
        for i in issued_books:
            p+="<p>"+i.book.title+" issued on "+i.b_date+"</p>"
        return HttpResponse(p)

