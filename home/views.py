from django.shortcuts import render
from django.http import HttpResponse,Http404,HttpResponseRedirect
from .models import *
from django.shortcuts import get_object_or_404
from instamojo_wrapper import Instamojo
from home import API_KEY,AUTH_TOKEN
from django.urls import reverse
from datetime import datetime
from django.contrib.auth import login, authenticate,logout
from .forms import SignUpForm
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
api = Instamojo(api_key=API_KEY, auth_token=AUTH_TOKEN, endpoint='https://test.instamojo.com/api/1.1/')

# Create your views here.
def test(request) :
    return render(request, 'home/profile.html')
def index(request):
    return render(request,'home/index.html')

def bookDetailView(request,bid):
    bk=get_object_or_404(Book,id=bid)
    rating=str(int(bk.rating))
    edition=bk.edition.strftime('%B') +" "+str(bk.edition.year)
    context={
        'book':bk,
        'rating':rating,
        'edition':edition,
    }
    return render(request,'home/single_product.html',context=context)
def catalogView(request):
    if request.method=="GET":
        pass
    else:
        books=Book.objects.all()
        p=""
        for i in books:
            p+="<p>"+book.title+"</p>"
        return HttpResponse(p)

@login_required
@csrf_exempt
def paymentView(request):
    template_name='home/checkout.html'
    if 'book_id' not in request.GET:
        raise Http404
    temp=int(request.GET['book_id'])
    bid=get_object_or_404(Book,id=temp)
    bk_instances=bid.bookinstance_set.filter(status=1)
    if(len(bk_instances)==0):
        raise Http404
    else:
        request.session['instance_id']=bk_instances[0]
    context={
        'book':bid,
        'balance':request.user.profile.balance,
    }
    if request.method=="POST":
        topay=bid.mrp
        balance=request.user.profile.balance
        if 'usebal' in request.POST:
            if(balance>bid.mrp):
                topay=0
            else:
                topay-=balance
                usr=request.user.profile
                usr.balance=0
                usr.save()
        if(topay>0):
            if(topay<10):
                topay=10
            response = api.payment_request_create(
                        amount=str(topay),
                        purpose="Rentafolio Book Rental",
                        send_email=False,
                        email=request.user.email,
                        buyer_name=request.user.username,
                        phone=request.user.profile.contact,
                        redirect_url=request.build_absolute_uri(reverse("checkout")),
                    )
                    
            return HttpResponseRedirect(response['payment_request']['longurl'])
        else:
            usr=request.user.profile
            usr.balance-=bid.mrp
            usr.save()
            request.session["book_purchased"]=True
            return HttpResponseRedirect(reverse('checkout'))
        book_instances=bid.bookinstance_set.all()
        for i in book_instances:
            if(i.status==1):
                i.borrower=request.user.profile
                i.b_date=datetime.now()
                i.status=0
                i.save()
                break
        return HttpResponseRedirect(reverse('checkout'))
    return render(request,template_name,context=context)

        

def profileView(request):

    return HttpResponse("profileView-OK")

def issuedView(request):
    if request.method=="POST":
        return_id=int(request.POST['return_id'])
        return_book=BookInstance.objects.get(id=return_id)
        return_book.borrower=None
        return_book.status=1
        return_book.save()
        days_issued=(datetime.now().date()-return_book.b_date.date()).days
        return_pct=0
        credit_pct=0
        if(days_issued<=30):
            return_pct=0.8
            credit_pct=0.1
        elif(days_issued<=60):
            return_pct=0.7
            credit_pct=0.15
        elif(days_issued<=180):
            credit_pct=0.25
            return_pct=0.5
        elif(days_issued<=360):
            return_pct=0.4
            credit_pct=0.3
        else:
            return_pct=0
            credit_pct=0.8
        usr=request.user.profile
        uploader=return_book.uploader
        usr.balance+=return_book.book.mrp*return_pct
        usr.save()
        uploader.balance+=credit_pct*return_book.book.mrp
        uploader.save()
        messages.warning(request,"Book successfully returned")
        return HttpResponse("OK")
    issued_books=request.user.profile.borrowed.all()
    p=""
    if len(issued_books)==0:
        return HttpResponse("You dont have any books issued")
    else:
        for i in issued_books:
            p+="<p>"+i.book.title+" issued on "+str(i.b_date.strftime("%-d %B, %Y"))+"</p>"
        return HttpResponse(p)


def signup(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()  # load the profile instance created by the signal
            user.profile.address = form.cleaned_data.get('address')
            user.profile.contact = form.cleaned_data.get('contact')
            user.profile.balance=0
            user.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            return HttpResponseRedirect(reverse('index'))
    else:
        form = SignUpForm()
    return render(request, 'home/signup.html', {'form': form})

def user_login(request):
    template_name='home/login.html'
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request,user)
                return HttpResponseRedirect(reverse('index'))
            else:
                return HttpResponse("Your account was inactive.")
        else:
            messages.warning(request,"Invalid Login Credentials")
            return render(request,template_name)
    else:
        return render(request, template_name)

@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))

def checkout(request):
    template_name='home/thanks.html'
    if request.session.get('book_purchased',False):
        return render(request,template_name)
    if 'payment_request_id' in request.GET and 'payment_id' in request.GET:
        try:
            payment_request_id=request.GET['payment_request_id']
            payment_id=request.GET['payment_id']
            response = api.payment_request_payment_status(payment_request_id, payment_id)
            pstatus=response['payment_request']['payment']['status']
            if(pstatus=="Failed"):
                return HttpResponse("Your Payment failed. Please go to the register page and try again")
            if(pstatus=="Credit"):
                instance_id=request.session.get('instance_id',-1)
                bk=get_object_or_404(BookInstance,id=instance_id)
                bk.status=0
                bk.borrower=request.user.profile
                bk.b_date=datetime.now()
                bk.save()
                del request.session['instance_id']
                return render(request,template_name)
        except:
            raise Http404
        raise Http404
    raise Http404