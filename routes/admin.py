import sqlite3
from flask import Blueprint, render_template, request, redirect, url_for, flash
import models

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/')
def index():
    return render_template('admin/index.html')


# ---- відгуки ----
@admin_bp.route('/feedback')
def feedback_list():
    return render_template('admin/feedback.html', items=models.get_all_feedback())


@admin_bp.route('/feedback/<int:id>/delete', methods=['POST'])
def feedback_delete(id):
    models.delete_feedback(id)
    return redirect(url_for('admin.feedback_list'))


# ---- товари ----
@admin_bp.route('/products')
def products():
    return render_template('admin/products.html', products=models.get_all_products())


@admin_bp.route('/products/new', methods=['GET', 'POST'])
def product_new():
    if request.method == 'POST':
        models.add_product(request.form['name'], request.form['description'],
                           float(request.form['price']), int(request.form['stock']))
        return redirect(url_for('admin.products'))
    return render_template('admin/product_form.html', product=None)


@admin_bp.route('/products/<int:id>/edit', methods=['GET', 'POST'])
def product_edit(id):
    if request.method == 'POST':
        models.update_product(id, request.form['name'], request.form['description'],
                              float(request.form['price']), int(request.form['stock']))
        return redirect(url_for('admin.products'))
    return render_template('admin/product_form.html', product=models.get_product(id))


@admin_bp.route('/products/<int:id>/delete', methods=['POST'])
def product_delete(id):
    try:
        models.delete_product(id)
    except sqlite3.IntegrityError:
        flash('Не можна видалити товар, який є в замовленнях')
    return redirect(url_for('admin.products'))


# ---- замовлення ----
@admin_bp.route('/orders')
def orders():
    orders = models.get_all_orders()
    items = {o['id']: models.get_order_items(o['id']) for o in orders}
    return render_template('admin/orders.html', orders=orders, items=items,
                           statuses=models.ORDER_STATUSES)


@admin_bp.route('/orders/<int:id>/status', methods=['POST'])
def order_status(id):
    status = request.form['status']
    if status in models.ORDER_STATUSES:
        models.update_order_status(id, status)
    return redirect(url_for('admin.orders'))


@admin_bp.route('/orders/<int:id>/delete', methods=['POST'])
def order_delete(id):
    models.delete_order(id)
    return redirect(url_for('admin.orders'))


# ---- клієнти (рівень 2) ----
@admin_bp.route('/clients')
def clients():
    return render_template('admin/clients.html', clients=models.get_all_clients())


@admin_bp.route('/clients/new', methods=['GET', 'POST'])
def client_new():
    if request.method == 'POST':
        try:
            models.add_client(request.form['name'], request.form['email'],
                              request.form['phone'])
            return redirect(url_for('admin.clients'))
        except sqlite3.IntegrityError:
            flash('Клієнт з таким email вже існує')
    return render_template('admin/client_form.html', client=None)


@admin_bp.route('/clients/<int:id>/edit', methods=['GET', 'POST'])
def client_edit(id):
    if request.method == 'POST':
        try:
            models.update_client(id, request.form['name'], request.form['email'],
                                 request.form['phone'])
            return redirect(url_for('admin.clients'))
        except sqlite3.IntegrityError:
            flash('Цей email вже використовується')
    return render_template('admin/client_form.html', client=models.get_client(id))


@admin_bp.route('/clients/<int:id>/delete', methods=['POST'])
def client_delete(id):
    try:
        models.delete_client(id)
    except sqlite3.IntegrityError:
        flash('Не можна видалити клієнта, у якого є замовлення')
    return redirect(url_for('admin.clients'))