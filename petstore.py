from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
#from enum import Enum
import json

#init app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:mysql@192.168.10.166/petstore'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)

#Status Class/Model
# noinspection PyUnresolvedReferences
class Status(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dis = db.Column(db.String(255))
    value = db.Column(db.String(10))
    pet_status = db.relationship('Pet', backref='status', lazy=True)
    order_status = db.relationship('Order', backref='status', lazy=True)

    def __init__(self, dis, value):
        self.dis = dis
        self.value = value

class StatusSchema(ma.Schema):
    class Meta:
        fields = ('id', 'dis', 'value')

status_schema = StatusSchema()
statuses_schema = StatusSchema(many=True)

#Category Class/Model
# noinspection PyUnresolvedReferences
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cat_name = db.Column(db.String(100), unique=True)
    pet_category = db.relationship('Pet', backref='category', lazy=True)

    def __init__(self, cat_name):
        self.cat_name = cat_name

class CategorySchema(ma.Schema):
    class Meta:
        fields = ('id', 'cat_name')

category_schema = CategorySchema()
categories_schema = CategorySchema(many=True)

#Order Class/Model
# noinspection PyUnresolvedReferences
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pet_id = db.Column(db.Integer)
    quantity = db.Column(db.Integer)
    shipdate = db.Column(db.DateTime, default=datetime.utcnow)
    complete = db.Column(db.Boolean, default=False)
    status_id = db.Column(db.Integer, db.ForeignKey('status.id'))

    def __init__(self, pet_id, quantity, shipdate, complete, status_id):
        self.pet_id = pet_id
        self.quantity = quantity
        self.shipdate = shipdate
        self.complete = complete
        self.status_id = status_id

class OrderSchema(ma.Schema):
    class Meta:
        fields = ('id', 'pet_id', 'quantity', 'shipdate', 'complete', 'status_id')

order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)

# noinspection PyUnresolvedReferences
tags = db.Table('tags',
                db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True),
                db.Column('pet_id', db.Integer, db.ForeignKey('pet.id'), primary_key=True)
)

# noinspection PyUnresolvedReferences
class Pet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pet_name = db.Column(db.String(20))
    photoURLs = db.relationship('PhotoURL', backref='pet', lazy=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    status_id = db.Column(db.Integer, db.ForeignKey('status.id'))
    tags = db.relationship('Tag', secondary=tags, lazy='subquery', backref=db.backref('tags', lazy=True))

    def __init__(self, pet_name, category_id, status_id):
        self.pet_name = pet_name
        self.category_id = category_id
        self.status_id = status_id

class PetSchema(ma.Schema):
    class Meta:
        fields = ('id', 'pet_name', 'category_id', 'status_id')

pet_schema = PetSchema()
pets_schema = PetSchema(many=True)

#Tag Class/Model
# noinspection PyUnresolvedReferences
class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag_name = db.Column(db.String(100))

    def __init__(self, tag_name):
        self.tag_name = tag_name

class TagSchema(ma.Schema):
    class Meta:
        fields = ('id', 'tag_name')

tag_schema = TagSchema()
tags_schema = TagSchema(many=True)

#PhotoURLs Class/Model
# noinspection PyUnresolvedReferences
class PhotoURL(db.Model):
    url = db.Column(db.String(255), primary_key=True)
    pet_id = db.Column(db.Integer, db.ForeignKey('pet.id'))

    def __init__(self, url, pet_id):
        self.url = url
        self.pet_id = pet_id

class PhotoURLsSchema(ma.Schema):
    class Meta:
        fields = ('url', 'pet_id')

photourl_schema = PhotoURLsSchema()
photourls_schema = PhotoURLsSchema(many=True)

#User Class/Model
# noinspection PyUnresolvedReferences
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    firstname = db.Column(db.String(20))
    lastname = db.Column(db.String(20))
    email = db.Column(db.String(40))
    password = db.Column(db.String(100))
    phone = db.Column(db.String(10))
    userstatus = db.Column(db.Integer)

    def __init__(self, username, firstname, lastname, email, password, phone, userstatus):
        self.username = username
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.password = password
        self.phone = phone
        self.userstatus = userstatus

class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'username', 'firstname', 'lastname', 'email', 'password', 'phone', 'userstatus')

user_schema = UserSchema()
users_schema = UserSchema(many=True)

#Create a status
@app.route('/status', methods=['POST'])
def add_status():
    dis = request.json['dis']
    value = request.json['value']

    new_status = Status(dis, value)
    db.session.add(new_status)
    db.session.commit()

    return status_schema.jsonify(new_status)

#Get all status
@app.route('/status', methods=['GET'])
def get_statuses():
    all_status = Status.query.all()
    result = statuses_schema.dump(all_status)
    return jsonify(result)

#Get one status
@app.route('/status/<id>', methods=['GET'])
def get_status(id):
    status = Status.query.get(id)
    return status_schema.jsonify(status)

#Create a status
@app.route('/tag', methods=['POST'])
def add_tag():
    tag_name = request.json['tag_name']
    new_tag = Tag(tag_name)
    db.session.add(new_tag)
    db.session.commit()

    return tag_schema.jsonify(new_tag)

#Get tags
@app.route('/tag', methods=['GET'])
def get_tags():
    tags = Tag.query.all()
    result = tags_schema.dump(tags)
    return tags_schema.jsonify(result)

#Get one status
@app.route('/tag/<id>', methods=['GET'])
def get_tag(id):
    tag = Status.query.get(id)
    return tag_schema.jsonify(tag)

@app.route('/tag_pet', methods=['POST'])
def add_tag_to_pet():
    pet_id = request.json['pet_id']
    tag_id = request.json['tag_id']
    pet = Pet.query.get(pet_id)
    tag = Tag.query.get(tag_id)

    tag.tags.append(pet)
    db.session.commit()

    tags = Pet.query.with_parent(tag)
    result = pets_schema.dump(tags)

    return pets_schema.jsonify(result)


#Create a category
@app.route('/category', methods=['POST'])
def add_category():
    cat_name = request.json['cat_name']
    new_category = Category(cat_name)
    db.session.add(new_category)
    db.session.commit()

    return category_schema.jsonify(new_category)

#Get all categories
@app.route('/category', methods=['GET'])
def get_categories():
    categories = Category.query.all()
    result = categories_schema.dump(categories)
    return categories_schema.jsonify(result)

#Get one category
@app.route('/category/<id>', methods=['GET'])
def get_category(id):
    category = Category.query.get(id)
    return category_schema.jsonify(category)

#Create a order
@app.route('/order', methods=['POST'])
def add_order():
    pet_id = request.json['pet_id']
    quantity = request.json['quantity']
    shipdate = datetime.strptime(request.json['shipdate'], "%Y-%m-%d %H:%M:%S")
    complete = request.json['complete']
    status_id = request.json['status_id']

    new_order = Order(pet_id, quantity, shipdate, complete, status_id)
    db.session.add(new_order)
    db.session.commit()

    return order_schema.jsonify(new_order)

#Get all orders
@app.route('/order', methods=['GET'])
def get_orders():
    orders = Order.query.all()
    result = orders_schema.dump(orders)
    return orders_schema.jsonify(result)

#Get one order
@app.route('/order/<id>', methods=['GET'])
def get_order(id):
    order = Order.query.get(id)
    return order_schema.jsonify(order)

#Create a pet
@app.route('/pet', methods=['POST'])
def add_pet():
    pet_name = request.json['pet_name']
    category_id = request.json['category_id']
    status_id = request.json['status_id']

    new_pet = Pet(pet_name, category_id, status_id)
    db.session.add(new_pet)
    db.session.commit()

    return pet_schema.jsonify(new_pet)

#Update a pet
@app.route('/pet/<id>', methods=['PUT'])
def update_pet(id):
    pet = Pet.query.get(id)
    pet_name = request.json['pet_name']
    category_id = request.json['category_id']
    status_id = request.json['status_id']

    pet.pet_name = pet_name
    pet.category_id = category_id
    pet.status_id = status_id

    db.session.commit()
    return pet_schema.jsonify(pet)

#Get all pets
@app.route('/pet', methods=['GET'])
def get_pets():
    pets = Pet.query.all()
    result = pets_schema.dump(pets)
    return pets_schema.jsonify(result)

#Get one pet
@app.route('/pet/<id>', methods=['GET'])
def get_pet(id):
    pet = Pet.query.get(id)
    return pet_schema.jsonify(pet)

#Create a photourl
@app.route('/pet/photourl', methods=['POST'])
def add_photourl():
    url = request.json['url']
    pet_id = request.json['pet_id']

    new_url = PhotoURL(url, pet_id)
    db.session.add(new_url)
    db.session.commit()

    return photourl_schema.jsonify(new_url)

#Get all photourls
@app.route('/pet/photourl', methods=['GET'])
def get_photourls():
    urls = PhotoURL.query.all()
    result = photourls_schema.dump(urls)

    return photourls_schema.jsonify(result)

#Get one photourl
@app.route('/pet/photourl/<id>', methods=['GET'])
def get_photourl(id):
    url = PhotoURL.query.get(id)

    return photourl_schema.jsonify(url)

#Create a user
@app.route('/user', methods=['POST'])
def add_user():
    username = request.json['username']
    firstname = request.json['firstname']
    lastname = request.json['lastname']
    email = request.json['email']
    password = generate_password_hash(request.json['password'], method='sha256')
    phone = request.json['phone']
    userstatus = request.json['userstatus']

    new_user = User(username, firstname, lastname, email, password, phone, userstatus)
    db.session.add(new_user)
    db.session.commit()

    return user_schema.jsonify(new_user)

#Update a product
@app.route('/user/<id>', methods=['PUT'])
def update_user(id):
    user = User.query.get(id)
    username = request.json['username']
    firstname = request.json['firstname']
    lastname = request.json['lastname']
    email = request.json['email']
    password = generate_password_hash(request.json['password'], method='sha256')
    phone = request.json['phone']
    userstatus = request.json['userstatus']

    user.username = username
    user.firstname = firstname
    user.lastname = lastname
    user.email = email
    user.password = password
    user.phone = phone
    user.userstatus = userstatus

    db.session.commit()

    return user_schema.jsonify(user)

#Get all users
@app.route('/user', methods=['GET'])
def get_users():
    all_users = User.query.all()
    result = users_schema.dump(all_users)
    return jsonify(result)

#Get one user
@app.route('/user/<id>', methods=['GET'])
def get_user(id):
    user = User.query.get(id)
    return user_schema.jsonify(user)

@app.route('/user/<id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get(id)
    db.session.delete(user)
    db.session.commit()
    return user_schema.jsonify(user)

if __name__ == "__main__":
    app.run(debug=True)

