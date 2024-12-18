import telebot
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.views import View

from .forms import RegistrationForm
from .models import Category, Product, Cart

bot = telebot.TeleBot('8084031453:AAHBKdLezF3nTat5OIxsaCbC3j_m_KjDt7U')


def home_page(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    context = {'products': products, 'categories': categories}

    return render(request, 'home.html', context)


def product_page(request, pk):
    product = Product.objects.get(id=pk)
    context = {'product': product}

    return render(request, 'product.html', context)


def category_page(request, pk):
    category = Category.objects.get(id=pk)
    products = Product.objects.filter(category=category)
    context = {'category': category, 'products': products}

    return render(request, 'category.html', context)


class Register(View):
    template_name = 'registration/register.html'

    def get(self, request):
        context = {'form': RegistrationForm}
        return render(request, self.template_name, context)

    def post(self, request):
        form = RegistrationForm(request.POST)

        if form.is_valid():
            username = form.clean_username()
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password2')
            user = User.objects.create_user(username=username,
                                            email=email,
                                            password=password)
            user.save()
            login(request, user)

            return redirect('/')

        context = {'form': form, 'message': 'Password or email is incorrect'}
        return render(request, self.template_name, context)


def search(request):
    if request.method == 'POST':
        product = request.POST.get('search')

        if Product.objects.get(title__iregex=product):
            result = Product.objects.get(title__iregex=product)
            return redirect(f'product/{result.id}')
        return redirect('/')


def logout_view(request):
    logout(request)
    return redirect('/')


def add_to_cart(request, pk):
    if request.method == 'POST':
        product = Product.objects.get(id=pk)

        if product.quantity >= int(request.POST.get('quantity')):
            Cart.objects.create(user_id=request.user.id,
                                user_product=product,
                                quantity=int(request.POST.get('quantity'))
                                ).save()
            return redirect('/')


def delete_from_cart(request, pk):
    product = Product.objects.get(id=pk)
    Cart.objects.filter(user_product=product).delete()

    return redirect('/cart')


def cart_page(request):
    user_cart = Cart.objects.filter(user_id=request.user.id)
    cart_products_ids = [cart_product.user_product.id for cart_product in
                         user_cart]
    quantities = [cart_product.quantity for cart_product in user_cart]
    quantities_available = [cart_product.user_product.quantity for cart_product
                            in user_cart]
    totals = [round(cart_product.quantity * cart_product.user_product.price, 2)
              for cart_product in user_cart]
    text = (f'New order\n'
            f'Client: {User.objects.get(id=request.user.id).email}\n\n')

    if request.method == 'POST':
        for i in range(len(cart_products_ids)):
            product = Product.objects.get(id=cart_products_ids[i])
            product.quantity = quantities_available[i] - quantities[i]
            product.save(update_fields=['quantity'])

        for j in user_cart:
            text += (f'Product: {j.user_product}\n'
                     f'Quantity: {j.quantity}\n--------------------\n')

        text += f'Total: ${round(sum(totals), 2)}'
        bot.send_message(62828291, text)
        user_cart.delete()

        return redirect('/')

    context = {'cart': user_cart, 'total': round(sum(totals), 2)}
    return render(request, 'cart.html', context)
