from flask import Blueprint, Flask, render_template, url_for, request, session, flash, redirect
from .models import Category, Book, Order
from .forms import CheckoutForm
from datetime import datetime
from . import db
import pickle

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
     if 'base_category' not in session:
          # Query the database to get a list of Category objects
          categories = Category.query.order_by(Category.name).all()

          # Create a list of dictionaries containing 'id' and 'name' attributes of each Category object
          category_list = [{'id': category.id, 'name': category.name} for category in categories]
          session['base_category'] = category_list
     return render_template('index.html')

@main_bp.route('/books/<int:category_id>')
def book(category_id):
     books = Book.query.filter(Book.category_id==category_id)
     category = Category.query.filter(Category.id == category_id).first()
     return render_template('book.html', books=books, category = category)


@main_bp.route('/books/')
def search():
     search = request.args.get('search')
     search = "%{}%".format(search)
     books = Book.query.filter(Book.description.like(search) | Book.title.like(search) | Book.author.like(search)).all()
     category = {"name": "Search Result..."}
     return render_template('book.html', books=books, category= category)


@main_bp.route('/bookdetails/<int:book_id>')
def bookdetail(book_id):
     bookdetail = Book.query.filter(Book.id == book_id).first()
     return render_template('bookdetails.html', bookdetail=bookdetail)


# Referred to as "Basket" to the user
@main_bp.route('/order', methods=['POST','GET'])
def order():
     book_id = request.values.get('book_id')

     # retrieve order if there is one
     if 'order_id'in session.keys():
          order = Order.query.get(session['order_id'])
          print("yes order exist ")
          # order will be None if order_id stale
     else:
          # there is no order
          order = None

     # create new order if needed
     if order is None:
          order = Order(status = False, firstname='', surname='', email='', phone='', totalcost=0, date=datetime.now())
          try:
               db.session.add(order)
               db.session.commit()
               print(order)
               session['order_id'] = order.id
          except Exception as e:
               print('Oops!! failed at creating a new order, aaya error che bhai')
               order = None

     # calcultate totalprice
     total_price = 0
     if order is not None:
          for book in order.bookdetails:
               total_price = total_price + book.price

     # are we adding an item?
     if book_id is not None and order is not None:
          book = Book.query.get(book_id)
          print(book)
          if book not in order.bookdetails:
               try:
                    order.bookdetails.append(book)
                    db.session.commit()
               except:
                    return 'There was an issue adding the item to your basket'
               return redirect(url_for('main.order'))
          else:
               flash('Item already in basket.')
               return redirect(url_for('main.order'))
     print(order)
     return render_template('order.html', order = order, total_price=total_price)


# Delete specific basket items
@main_bp.route('/deleteorderitem', methods=['POST'])
def deleteorderitem():
    id=request.form['id']
    if 'order_id' in session:
        order = Order.query.get_or_404(session['order_id'])
        book_to_delete = Book.query.get(id)
        try:
            order.bookdetails.remove(book_to_delete)
            db.session.commit()
            return redirect(url_for('main.order'))
        except:
            return 'Problem deleting item from order'
    return redirect(url_for('main.order'))


# Scrap basket
@main_bp.route('/deleteorder')
def deleteorder():
    if 'order_id' in session:   
        del session['order_id']
        flash('All items deleted')
    return redirect(url_for('main.index'))

@main_bp.route('/checkout', methods=['POST','GET'])
def checkout():
     form = CheckoutForm() 
     
     if 'order_id' in session:
          order = Order.query.get_or_404(session['order_id'])
          
          if request.method == 'POST':
               order.status = True
               order.firstname = form.firstname.data
               order.surname = form.surname.data
               order.email = form.email.data
               order.phone = form.phone.data
               totalcost = 0
               for book in order.bookdetails:
                    totalcost = totalcost + book.price
               order.totalcost = totalcost
               order.date = datetime.now()
               try:
                    db.session.commit()
                    del session['order_id']
                    flash('Thank you! One of our awesome team members will contact you soon...')
                    return redirect(url_for('main.index'))
               except:
                    return 'There was an issue completing your order'
     return render_template('checkout.html', form=form)
