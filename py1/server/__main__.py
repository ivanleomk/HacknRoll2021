from flask import Flask, jsonify
import os

from sqlalchemy import create_engine,text,inspect,Column, ForeignKey, Integer,Text,exc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import pytz
from datetime import datetime

from collections import defaultdict;
import sys

app = Flask(__name__)
Base = declarative_base()

time_zone = pytz.timezone('Asia/Singapore')



#BASE OBJECTS
class User(Base):
    __tablename__ = 'users'

    user_id = Column(Integer,primary_key=True)
    user_location = Column(Text)

class OrderRestaurant(Base):
    __tablename__ = 'restaurants'
    restaurant_id = Column(Integer,primary_key = True)
    restaurant_name = Column(Text)

class Order(Base):
    __tablename__ = 'orders'
    
    order_id = Column(Integer,primary_key=True)
    restaurant_id = Column(Integer,ForeignKey('restaurants.restaurant_id'))
    order_cutoff = Column(Integer)
    user_id = Column(Text,ForeignKey('user.user_id'))

class RestaurantTag(Base):
    __tablename__ = "restaurantTags"

    id = Column(Integer,primary_key = True)
    restaurant_id = Column(Integer,ForeignKey('restaurants.restaurant_id'))
    user_id = Column(Text,ForeignKey('user.user_id'))

def logging_variables(var):
    print(var,file = sys.stderr)

engine = create_engine('postgresql://ynchacks:password@db:5433/ynchacks')
Session = sessionmaker(bind=engine)
inspector = inspect(engine)
session = Session()

def get_current_time():
    my_time = datetime.utcnow()

    current_time_aware = my_time.astimezone(time_zone)
    
    current_time_stripped = datetime.strftime(current_time_aware,"%Y-%m-%d %H:%M:%S")
    current_time = datetime.strptime(current_time_stripped,'%Y-%m-%d %H:%M:%S')

    return current_time


@app.route("/alchemy_version")
def alchemy_version():
    version = sqlalchemy.__version__
    return jsonify(hello="We are currently running {}".format(version))



@app.route("/restaurants/get_restaurants")
def get_restaurants():
    with engine.connect() as con:
        res = con.execute('SELECT * FROM restaurants')
    restaurants = []
    for rowproxy in res:
        (user_id,location) = rowproxy
        restaurants.append(tuple((user_id,location)))
    return jsonify(restaurants) 

@app.route("/orders/add_order/<restaurantId>/<orderCutOff>/<userId>")
def add_order(restaurantId,orderCutOff,userId):
    """
    orderCutOff must be in the format HH:MM
    """
    try:
        formatted_order = datetime.today().strftime('%Y-%m-%d')
        formatted_time = "{}-{}:00".format(formatted_order,orderCutOff)
        data = [{'restaurant_id':restaurantId, "order_cutoff":formatted_time, "user_id": userId}]
        statement = text(
            """
            INSERT INTO orders  ("restaurant_id","order_cutoff","user_id")
            VALUES (:restaurant_id,:order_cutoff,:user_id)
            """
        )
        with engine.connect() as con:
            for line in data:
                con.execute(statement, **line)
        
        
        session.commit()
        return jsonify({"Message":"Success!"})
    except exc.SQLAlchemyError:
        return jsonify({"Message":"Order has already been added to database"})


@app.route("/orders/get_orders/")
def get_orders():
    try:
        
        
        state = text("""
            SELECT 
            m.*,
            users.user_location
            FROM
            (SELECT 
            orders.*,
            restaurants.restaurant_name
            FROM orders
            LEFT OUTER JOIN
            restaurants 
            ON 
            orders.restaurant_id = restaurants.restaurant_id
            ) as m
            LEFT OUTER JOIN
            users
            on 
            m.user_id = users.user_id;
        """)
        with engine.connect() as con:
            res = con.execute(state)

        orders = []
        for rowproxy in res:
            (order_id,restaurant_id,order_cutoff,user_id,restaurant_name,user_location) = rowproxy
            cutoff = datetime.strptime(order_cutoff,'%Y-%m-%d-%H:%M:%S')

            if(cutoff > get_current_time()):
                orders.append(
                    {
                        "user_id":user_id,
                        "restaurant_name":restaurant_name,
                        "order_cutoff":order_cutoff,
                        "location":user_location
                    }
                )
            else:
                logging_variables(cutoff)

        return jsonify(orders)
    except exc.SQLAlchemyError:
        return jsonify({"Message":"Order has already been added to database"})

#
##
#
#
## USER ROUTES 
#
#
##
#


@app.route("/users/add_user/<userId>/<userLocation>")
def add_user(userId,userLocation):
    """
    Adding a user, requires the params UserID and userLocation
    """
    session.add(User(user_id = userId,user_location = userLocation))
    try:
        session.commit()
        return jsonify({"Message":"Success!"})
    except exc.SQLAlchemyError:
        return jsonify({"Message":"User Already Exists in Database"})


@app.route("/users/get_users")
def get_users():
    """
    get List of current users
    """
    with engine.connect() as con:
        res = con.execute('SELECT * FROM users')
    users = []
    for rowproxy in res:
        (user_id,location) = rowproxy
        users.append(tuple((user_id,location)))
    return jsonify(users)  
    

@app.route("/check_table")
def check_table():
    res = defaultdict(list)
    for table_name in inspector.get_table_names():
        print("Currently looking at  {}".format(table_name),file = sys.stderr)
        for column in inspector.get_columns(table_name):
            print(column['name'],file = sys.stderr)
        print("",file = sys.stderr)
    
    # print(res, file=sys.stderr)
    return {}

if __name__ == '__main__':
    port = os.environ['PORT']
    app.run(host='0.0.0.0', port=port)
