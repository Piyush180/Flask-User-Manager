from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///people.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(300), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()


@app.route('/', methods=['GET', 'POST'])
def index():
    # Add Entry
    if request.method == 'POST':
        name = request.form['name'].strip()
        address = request.form['address'].strip()

        if not name or not address:
            return "ERROR: Name and Address required!"

        new_person = Person(name=name, address=address)
        db.session.add(new_person)
        db.session.commit()
        return redirect('/')

    # Search Filter
    search_query = request.args.get('search')

    if search_query:
        people = Person.query.filter(
            (Person.name.contains(search_query)) |
            (Person.address.contains(search_query))
        ).order_by(Person.date_added.desc()).all()
    else:
        people = Person.query.order_by(Person.date_added.desc()).all()

    return render_template('index.html', people=people)


@app.route('/delete/<int:id>')
def delete(id):
    person = Person.query.get_or_404(id)
    db.session.delete(person)
    db.session.commit()
    return redirect('/')


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    person = Person.query.get_or_404(id)

    if request.method == 'POST':
        person.name = request.form['name']
        person.address = request.form['address']
        db.session.commit()
        return redirect('/')

    return render_template('update.html', person=person)

@app.route('/search')
def search():
    query = request.args.get('query')

    if query:
        people = Person.query.filter(
            (Person.name.contains(query)) |
            (Person.address.contains(query))
        ).order_by(Person.date_added.desc()).all()
    else:
        people = Person.query.order_by(Person.date_added.desc()).all()

    # Return only table rows HTML
    return render_template('search.html', people=people)




if __name__ == "__main__":
    app.run(debug=True)
