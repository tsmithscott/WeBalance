from models import Companies, Employees, Employers, Preferences, Records, Users
from werkzeug.security import generate_password_hash


def insert_mock_data(db):
    # Create and add companies
    db.session.add(Companies('Acme Corporation', '5 The Lindens', 'Floor 12', 'B1 1BZ', 'Birmingham', 'England'))
    db.session.add(Companies('Globex Corporation', '29 Dowgate Road', 'Floor 2', 'B1 1DA', 'Birmingham', 'England'))
    db.session.add(Companies('Soylent Corp', '35 Park Manor Farm', 'Floor 7', 'M1 1AD', 'Manchester', 'England'))
    db.session.add(Companies('Initech', '10 Tunbeck Road', 'Floor 6', 'N21 1RT', 'London', 'England'))
    db.session.add(Companies('Hooli', '12 Kirby Road', 'Floor 15', 'NE1 1AA', 'Newcastle', 'England'))
    db.session.commit()
    # Create and add users for employers
    db.session.add(Users('acme@acorporation.com', generate_password_hash("password", method='sha256'), 'John', 'Smith', True))
    db.session.add(Users('globex@glo.com', generate_password_hash("password", method='sha256'), 'Jane', 'Doe', True))
    db.session.add(Users('soy@lent.com', generate_password_hash("password", method='sha256'), 'David', 'Foster', True))
    db.session.add(Users('ini@tech.com', generate_password_hash("password", method='sha256'), 'Patrick', 'Bateman', True))
    db.session.add(Users('hooli@pied.piper', generate_password_hash("password", method='sha256'), 'John', 'Price', True))
    db.session.commit()
    # Create and add employers
    db.session.add(Employers(1, 1))
    db.session.add(Employers(2, 2))
    db.session.add(Employers(3, 3))
    db.session.add(Employers(4, 4))
    db.session.add(Employers(5, 5))
    db.session.commit()
    # Create and add users for employees
    db.session.add(Users('willstrop@acorporation.com', generate_password_hash("password", method='sha256'), 'Korie', 'Willstrop', False))
    db.session.add(Users('bastow@acorporation.com', generate_password_hash("password", method='sha256'), 'Junie', 'Bastow', False))
    db.session.add(Users('selesnick@glo.com', generate_password_hash("password", method='sha256'), 'Libbie', 'Selesnick', False))
    db.session.add(Users('mattacks@glo.com', generate_password_hash("password", method='sha256'), 'Ora', 'Mattacks', False))
    db.session.add(Users('gotmann@lent.com', generate_password_hash("password", method='sha256'), 'Justinian', 'Gotmann', False))
    db.session.add(Users('daveren@lent.com', generate_password_hash("password", method='sha256'), 'Carolynn', 'Daveren', False))
    db.session.add(Users('bathoe@tech.com', generate_password_hash("password", method='sha256'), 'Michaella', 'Bathoe', False))
    db.session.add(Users('charnley@tech.com', generate_password_hash("password", method='sha256'), 'Cleavland', 'Charnley', False))
    db.session.add(Users('simonou@pied.piper', generate_password_hash("password", method='sha256'), 'Heindrick', 'Simonou', False))
    db.session.add(Users('dunstan@pied.piper', generate_password_hash("password", method='sha256'), 'Dannye', 'Dunstan', False))
    db.session.commit()
    # Create and add employees
    db.session.add(Employees(6, 1))
    db.session.add(Employees(7, 1))
    db.session.add(Employees(8, 2))
    db.session.add(Employees(9, 2))
    db.session.add(Employees(10, 3))
    db.session.add(Employees(11, 3))
    db.session.add(Employees(12, 4))
    db.session.add(Employees(13, 4))
    db.session.add(Employees(14, 5))
    db.session.add(Employees(15, 5))
    db.session.commit()
    # Create and add preferences for employers
    db.session.add(Preferences(1, 32, 30, 10))
    db.session.add(Preferences(2, 36, 25, 15))
    db.session.add(Preferences(3, 30, 20, 5))
    db.session.add(Preferences(4, 20, 15, 2))
    db.session.add(Preferences(5, 25, 35, 20))
    db.session.commit()
    # Create and add preferences for employees
    db.session.add(Preferences(6, 32, 30, 10))
    db.session.add(Preferences(7, 36, 25, 15))
    db.session.add(Preferences(8, 30, 20, 5))
    db.session.add(Preferences(9, 20, 15, 17))
    db.session.add(Preferences(10, 25, 35, 20))
    db.session.add(Preferences(11, 32, 30, 10))
    db.session.add(Preferences(12, 36, 25, 15))
    db.session.add(Preferences(13, 30, 20, 5))
    db.session.add(Preferences(14, 20, 15, 3))
    db.session.add(Preferences(15, 25, 35, 20))
    db.session.commit()