from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from configuration import SENTRY_DSN
import sentry_sdk

sentry_sdk.init(
    dsn=SENTRY_DSN,
    send_default_pii=True,
)

app = Flask(__name__)
# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///patients.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Patient model
class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    diagnosis = db.Column(db.String(200), nullable=True)

    def to_dict(self):
        return dict(id=self.id, name=self.name, age=self.age, gender=self.gender, diagnosis=self.diagnosis)

# Create the database
with app.app_context():
    db.create_all()

# Create patient
@app.route('/patients', methods=['POST'])
def create_patient():
    data = request.get_json()
    new_patient = Patient(
        name=data['name'],
        age=data['age'],
        gender=data['gender'],
        diagnosis=data.get('diagnosis', '')
    )
    db.session.add(new_patient)
    db.session.commit()
    return jsonify(new_patient.to_dict()), 201

# Get all patients
@app.route('/patients', methods=['GET'])
def get_patients():
    patients = Patient
    return jsonify([patient.to_dict() for patient in patients])

# Get a specific patient by ID
@app.route('/patients/<int:patient_id>', methods=['GET'])
def get_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    return jsonify(patient.to_dict())

# Update a patient
@app.route('/patients/<int:patient_id>', methods=['PUT'])
def update_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    data = request.get_json()
    patient.name = data.get('name', patient.name)
    patient.age = data.get('age', patient.age)
    patient.gender = data.get('gender', patient.gender)
    patient.diagnosis = data.get('diagnosis', patient.diagnosis)
    db.session.commit()
    return jsonify(patient.to_dict())

# Delete a patient
@app.route('/patients/<int:patient_id>', methods=['DELETE'])
def delete_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    db.session.delete(patient)
    db.session.commit()
    return jsonify({'message': 'Patient deleted successfully'})

if __name__ == '__main__':
    app.run(debug=True)
