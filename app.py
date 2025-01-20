from flask import Flask, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash
import pandas as pd
import io

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Model
class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    date_added = db.Column(db.Date, nullable=False)
    price = db.Column(db.Float, nullable=False)
    condition = db.Column(db.String(100), nullable=False)

# List of allowed emails
ALLOWED_EMAILS = [
    'user1@example.com', 'user2@example.com', 'user3@example.com',
    'user4@example.com', 'user5@example.com', 'user6@example.com',
    'user7@example.com', 'user8@example.com', 'user9@example.com',
    'user10@example.com'
]

# Hardcoded password hash for demonstration purposes
PASSWORD_HASH = 'pbkdf2:sha256:150000$example$e9c9b1b7c31b4fbb3150c9c1f8c7a30e9c8db3edc1d78a8f08ff65c20ff33f6c'

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    if data['email'] in ALLOWED_EMAILS and check_password_hash(PASSWORD_HASH, data['password']):
        return jsonify({'message': 'Login successful'}), 200
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/add_item', methods=['POST'])
def add_item():
    data = request.json
    new_item = Inventory(
        item_name=data['item_name'],
        quantity=data['quantity'],
        date_added=data['date_added'],
        price=data['price'],
        condition=data['condition']
    )
    db.session.add(new_item)
    db.session.commit()
    return jsonify({'message': 'Item added successfully'}), 201

@app.route('/get_inventory', methods=['GET'])
def get_inventory():
    items = Inventory.query.all()
    inventory_list = [{
        'id': item.id,
        'item_name': item.item_name,
        'quantity': item.quantity,
        'date_added': item.date_added.strftime('%Y-%m-%d'),
        'price': item.price,
        'condition': item.condition
    } for item in items]
    return jsonify(inventory_list), 200

@app.route('/update_item/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    data = request.json
    item = Inventory.query.get(item_id)
    if item:
        item.item_name = data['item_name']
        item.quantity = data['quantity']
        item.date_added = data['date_added']
        item.price = data['price']
        item.condition = data['condition']
        db.session.commit()
        return jsonify({'message': 'Item updated successfully'}), 200
    return jsonify({'message': 'Item not found'}), 404

@app.route('/delete_item/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    item = Inventory.query.get(item_id)
    if item:
        db.session.delete(item)
        db.session.commit()
        return jsonify({'message': 'Item deleted successfully'}), 200
    return jsonify({'message': 'Item not found'}), 404

@app.route('/download_inventory', methods=['GET'])
def download_inventory():
    condition_filter = request.args.get('condition', None)
    query = Inventory.query

    if condition_filter:
        query = query.filter_by(condition=condition_filter)
    
    items = query.all()
    data = [{
        'Item Name': item.item_name,
        'Quantity': item.quantity,
        'Date Added': item.date_added.strftime('%Y-%m-%d'),
        'Price': item.price,
        'Condition': item.condition
    } for item in items]

    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Inventory')
        writer.save()
    output.seek(0)

    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', as_attachment=True, attachment_filename='inventory.xlsx')

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
