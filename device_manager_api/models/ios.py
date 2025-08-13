from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class IOSDevice(db.Model):
    __tablename__ = 'ios_devices'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    udid = db.Column(db.String(100), unique=True, nullable=False)
    status = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<IOSDevice {self.name} ({self.udid})>'

class IOSScreenshot(db.Model):
    __tablename__ = 'ios_screenshots'
    
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('ios_devices.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    image_path = db.Column(db.String(255), nullable=False)

    device = db.relationship('IOSDevice', backref='screenshots')

    def __repr__(self):
        return f'<IOSScreenshot {self.id} for Device {self.device_id}>'

class IOSAction(db.Model):
    __tablename__ = 'ios_actions'
    
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('ios_devices.id'), nullable=False)
    action_type = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)

    device = db.relationship('IOSDevice', backref='actions')

    def __repr__(self):
        return f'<IOSAction {self.action_type} for Device {self.device_id}>'