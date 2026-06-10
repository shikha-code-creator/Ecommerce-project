from django.http import HttpResponse
from django.shortcuts import render,redirect,get_object_or_404
from .models import *
#from django.contrib.auth.forms import UserCreationForm
from .forms import UserRegisterForm, CustomerForm
from django.contrib.auth import login,logout
from django.http import HttpResponse
from django.conf import settings
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import stripe


# Create your views here.
def index(request):
    prds=Product.objects.all()
    if request.user.is_authenticated == True:
        order,created = Order.objects.get_or_create(customer=request.user.customer,complete=False)
    else:
        order={"gettotqty":0}
    return render(request,"store/index.html",{"prds":prds,"order":order})

def register(request):
    if request.method=="POST":
        # usrfrm=UserCreationForm()
        usrfrm = UserRegisterForm(request.POST)
        cstfrm=CustomerForm(request.POST)
        if usrfrm.is_valid() and cstfrm.is_valid():
            user=usrfrm.save()
            customer=cstfrm.save(commit=False)
            customer.user=user
            customer.save()
            login(request, user)
        return redirect("index")
    else:
        usrfrm = UserRegisterForm(request.POST)
        cstfrm = CustomerForm(request.POST)
        return render(request,"registration/register.html",{"usrfrm":usrfrm,"cstfrm":cstfrm})

def logout1(request):
    logout(request)
    return redirect("/myauth/login")

def updatecart(request):
      if request.user.is_authenticated == True:
            if request.method == "POST":
                customer = request.user.customer
                order, created = Order.objects.get_or_create(customer=customer, complete=False)
                if request.POST.get("btnupd"):
                    ctrls = [ctrl for ctrl in request.POST if 'txtqty' in ctrl]
                    pid = (int)(ctrls[0][6:])
                    product = Product.objects.get(id=pid)
                    orderitm,created= OrderItems.objects.get_or_create(order=order, product=product)
                    qty = (int)(request.POST.get("txtqty" + str(pid)))
                    if qty > 0:
                        orderitm.quantity = qty
                        orderitm.save()
                    else:
                        orderitm.delete()

                elif request.POST.get("btndel"):
                    ctrls = [ctrl for ctrl in request.POST if 'txtqty' in ctrl]
                    pid = (int)(ctrls[0][6:])
                    product = Product.objects.get(id=pid)
                    orderitem,created = OrderItems.objects.get_or_create(order=order, product=product)
                    orderitem.delete()
                else:
                    ctrls = [ctrl for ctrl in request.POST if 'btn' in ctrl]
                    pid = (int)(ctrls[0][3:])
                    product = Product.objects.get(id=pid)
                    orderitem, created = OrderItems.objects.get_or_create(order=order, product=product)
                    orderitem.quantity = orderitem.quantity + 1
                    orderitem.save()
            return redirect("cart")
      else:
            return redirect("/myauth/login")

def cart(request):
    if request.user.is_authenticated == True:
        customer = request.user.customer
        order,created = Order.objects.get_or_create(customer=customer,complete=False)
        orditm = order.orderitems_set.all()
        return render(request,"store/cart.html",{"order":order,"orderitems":orditm})
    else:
        return redirect("/myauth/login")

def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        orditm = order.orderitems_set.all()
        return render(request, "store/checkout.html", {"order":order,"orderitems":orditm})
    else:
        return redirect("/myauth/login")


def product_detail(request, pk):
    # This finds the product or returns a 404 error if it doesn't exist
    product = get_object_or_404(Product, id=pk)
    return render(request, 'store/product_view.html', {'product': product})


@csrf_exempt
def stripe_config(request):
    if request.method == 'GET':
        stripe_config = {'publicKey': settings.STRIPE_PUBLISHABLE_KEY}
    return JsonResponse(stripe_config, safe=False)

@csrf_exempt
def create_checkout_session(request):
        if request.method == 'GET':
         domain_url = 'http://localhost:8000/'
         stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            lst=[]
            customer=request.user.customer
            order,created=Order.objects.get_or_create(customer=customer,complete=False)
            orditms=order.orderitems_set.all()
            for itm in orditms:
                lst.append(
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': itm.product.prdnam,
                        },
                        'unit_amount': (int)(itm.product.price*100),
                    },
                    'quantity': itm.quantity,
                },)
            print(lst)
            # ?session_id={CHECKOUT_SESSION_ID} means the redirect will have the session ID set as a query param
            checkout_session = stripe.checkout.Session.create(
                success_url=domain_url + 'success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=domain_url + 'cancelled/',
                payment_method_types=['card'],
                mode='payment',
                line_items=lst,
                metadata={
                    'cust':request.user.customer.id,
                    'addr':request.GET.get("query")
                }
            )
            return JsonResponse({'sessionId': checkout_session['id']})
        except Exception as e:
            return JsonResponse({'error': str(e)})

def SuccessView(request):
    return render(request,"store/success.html")

def CancelledView(request):
    return render(request,"store/Canpage.html")

@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    endpoint_secret = settings.STRIPE_ENDPOINT_SECRET
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)
    print("hello")
    # Handle the checkout.session.completed event
    print(event["type"])

    if event['type'] == 'checkout.session.completed':
        print("Payment was successful.")
        # TODO: run some custom code here
        #to update order status and to add shipping information
        session = event["data"]["object"]
        metadata=session.get("metadata",{})
        cid=metadata.get("cust")
        print(cid)
        addr=metadata.get("addr")
        print(addr)
        customer=Customer.objects.get(id=cid)
        order,created=Order.objects.get_or_create(customer=customer,complete=False)
        order.transaction_id=session.get("payment_intent")
        order.complete=True
        order.save()
        ad,ct,sta,zipcod=addr.split("|")
        ship=ShippingAddress.objects.create(customer=customer,order=order,address=ad,city=ct,state=sta,zipcode=zipcod)

    return HttpResponse(status=200)

def myorders(request):
    customer = request.user.customer
    orders = Order.objects.filter(customer=customer)
    orderitems = OrderItems.objects.filter(order__in=orders)
    context = {'orderitems': orderitems}
    return render(request, 'store/myorders.html', context)