import flask
from flask import request, json, jsonify
from flask_sqlalchemy import SQLAlchemy

#initial setup
app = flask.Flask(__name__)

app.config['SECRET_KEY'] = 'hardsecretkey'

# SqlAlchemy Database Configuration With Mysql
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:Heslo123@localhost/restaurants'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

#create data model
class restaurant(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    contact = db.Column(db.String(100))
    opening_hours = db.Column(db.String(100))
    adress = db.Column(db.String(100))
    food = db.relationship("food", backref="restaurant")

    def __repr__(self):
        return f'<restaurant "{self.name}">'

class food(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.String(100))
    food_name = db.Column(db.String(100))
    price = db.Column(db.String(100))
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'))

    def __repr__(self):
        return f'<food "{self.food_name}">'


app.app_context().push()

#endpoint for interacting with restaurant object
@app.route('/restaurant', methods=['POST','GET','PUT','DELETE'])
def restaurant_endpoint():
    if flask.request.method == 'POST':
        restaurant_instance = restaurant(name = request.form["name"],contact = request.form["contact"],opening_hours= request.form["opening_hours"],adress= request.form["adress"])
        db.session.add(restaurant_instance)
        db.session.commit()
        return "Restaurant added"
    elif flask.request.method == 'GET':
        which = request.args["get"]
        #return all restaurants from DB
        if which == "all":
            restaurant_data = restaurant.query.all()
            data_return = [{"name":i.name,"contact":i.contact,"opening_hours":i.opening_hours,"adress":i.adress} for i in restaurant_data]
            return jsonify(data_return)
        #return only 1 restaurant specified by it´s name
        else:
            instance = restaurant.query.filter_by(name='"' + which + '"').first()
            data_return = {"name":instance.name,"contact":instance.contact,"opening_hours":instance.opening_hours,"adress":instance.adress}
            return jsonify(data_return)
    elif flask.request.method == 'PUT':
        which = request.args["name"]
        update = restaurant.query.filter_by(name='"' + which + '"').first()
        #check which attributes need to be updated and update them
        for i in request.form.keys():
            if i == "name":
                update.name = request.form[i]
            if i == "contact":
                update.contact = request.form[i]
            if i == "opening_hours":
                update.opening_hours = request.form[i]
            if i == "adress":
                update.adress = request.form[i]
            db.session.commit()
        return "ok"
    #endpoint for deletion restaurant from DB
    else:
        which = request.args["name"]
        deleted = restaurant.query.filter_by(name='"' + which + '"').first()
        db.session.delete(deleted)
        db.session.commit()
        return jsonify({"name":deleted.name,"contact":deleted.contact,"opening_hours":deleted.opening_hours,"adress":deleted.adress})

@app.route('/food', methods=['POST','GET','PUT','DELETE'])
def food_endpoint():
    if flask.request.method in ["POST","PUT","DELETE"]:
        which = request.form["restaurant"]
        for_restaurant = restaurant.query.filter_by(name='"' + which + '"').first()
        #check if restaurant where user assigns the food exists in DB
        if for_restaurant is not None:
            if flask.request.method == 'POST':
                #loop throught the keys (days monday - friday) of request body, for each day create an instance of food object and push to DB
                for i in request.form.keys():
                    if request.form[i] != which:
                        item = json.loads(request.form[i])
                        menu = food(day= i , food_name= item["nazov"], price= item["cena"], restaurant=for_restaurant)
                        db.session.add(menu)
                        db.session.commit()
                return "menu added"
            elif flask.request.method == 'PUT':
                #filter on which restaurant and which day the attributes should be updated
                day = request.form["day"]
                res_id = restaurant.query.filter_by(name='"' + which + '"').first().id
                item = food.query.filter_by(restaurant_id= res_id, day = day ).first()
                #check which attributes should be updated and update them
                if "nazov" in request.form.keys():
                    item.food_name = request.form["nazov"]
                if "cena" in request.form.keys():
                    item.price = request.form["cena"]
                db.session.commit()
                return "food updated"
            else:
                #filter which item should be deleted and delete it from DB
                day = request.form["day"]
                res_id = restaurant.query.filter_by(name='"' + which + '"').first().id
                deleted = food.query.filter_by(restaurant_id=res_id, day=day).first()
                db.session.delete(deleted)
                db.session.commit()
                return jsonify({"day": deleted.day, "food_name": deleted.food_name, "price": deleted.price})
        else:
            #if restaurant is not in DB, user cannot insert menu to DB and assign it to restaurant
            return "restaurant is not in database"
    else:
        #if the method = GET, return menu of each day to the user
        which = request.args["restaurant"]
        res_id = restaurant.query.filter_by(name='"' + which + '"').first().id
        food_data = food.query.filter_by(restaurant_id= res_id ).all()
        data_return = [{"day": i.day, "food_name": i.food_name, "price": i.price} for i in food_data]
        return jsonify(data_return)

if __name__ == '__main__':
    app.run()