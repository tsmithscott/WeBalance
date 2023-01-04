import datetime

from faker import Faker
from werkzeug.security import generate_password_hash

from models import Companies, Employees, Employers, Preferences, Records, Users

fake = Faker()


def insert_mock_data(db):
    # Generate mock data for the Companies table
    for i in range(2):
        company = Companies(
            name=fake.company(),
            address_line_1=fake.street_address(),
            postcode=fake.postcode(),
            city=fake.city(),
            country=fake.country()
        )
        company.address_line_2 = fake.secondary_address()
        db.session.add(company)

    # Generate mock data for the Users table
    companies = Companies.query.all()
    for i in range(2):
        email_domain = companies[i].name.lower().replace(" ", "").replace(",", "")
        password = generate_password_hash('password', method='sha256')
        user = Users(
            email=f"employer@{email_domain}.com",
            password=password,
            firstname=fake.first_name(),
            surname=fake.last_name(),
            is_employer=True
        )
        db.session.add(user)

    for i in range(5):
        email_domain = companies[0].name.lower().replace(" ", "").replace(",", "")
        password = generate_password_hash('password', method='sha256')
        user = Users(
            email=f"employee{i+1}@{email_domain}.com",
            password=password,
            firstname=fake.first_name(),
            surname=fake.last_name(),
            is_employer=False
        )
        db.session.add(user)

    for i in range(5):
        email_domain = companies[1].name.lower().replace(" ", "").replace(",", "")
        password = generate_password_hash('password', method='sha256')
        user = Users(
            email=f"employee{i+1}@{email_domain}.com",
            password=password,
            firstname=fake.first_name(),
            surname=fake.last_name(),
            is_employer=False
        )
        db.session.add(user)
        
    # Generate mock data for the Employers table
    users = Users.query.all()
    for i in range(2):
        employer = Employers(
            user_id=users[i].id,
            company_id=companies[i].id
        )
        db.session.add(employer)

    # Generate mock data for the Employees table
    employers = Employers.query.all()
    for i in range(5):
        employee = Employees(
            user_id=users[i+2].id,
            employer_id=employers[0].id
        )
        db.session.add(employee)

    for i in range(5):
        employee = Employees(
            user_id=users[i+7].id,
            employer_id=employers[1].id
        )
        db.session.add(employee)

    # Generate mock data for the Preferences table
    for user in users:
        preference = Preferences(
            user_id=user.id,
            max_hours_weekly=fake.random_int(min=20, max=50),
            max_emails_daily=fake.random_int(min=10, max=20),
            max_calls_daily=fake.random_int(min=1, max=5)
        )
        db.session.add(preference)

    # Generate mock data for the Records table
    for employee in Employees.query.all():
        # Calculate the current and previous months
        now = datetime.datetime.now()
        current_month = now.month
        previous_month = current_month - 1 if current_month > 1 else 12
        current_year = now.year
        previous_year = current_year if current_month > 1 else current_year - 1

        for i in range(40):
            # Generate a random start time in the current or previous month
            start_date_str = f"{previous_year}-{previous_month}-01 00:00:00"
            end_date_str = f"{current_year}-{current_month}-{now.day} {now.hour}:{now.minute}:{now.second}"
            start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d %H:%M:%S")
            end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d %H:%M:%S")
            start_time = fake.date_time_between(start_date, end_date)
        
            # Generate a random end time on the same day as the start time, or a maximum of one day later
            end_time = fake.date_time_between(
                start_date=start_time,
                end_date=start_time + datetime.timedelta(days=1)
            )

            # Make sure the duration of the record is reasonable for a day's work (i.e. no more than 9 hours)
            while (end_time - start_time).total_seconds() > 36000 or (end_time - start_time).total_seconds() < 14400:
                end_time = fake.date_time_between(
                    start_date=start_time,
                    end_date=start_time + datetime.timedelta(days=1)
                )

            # Generate random number of emails and calls within reason
            emails_sent = fake.random_int(min=5, max=30)
            calls_made = fake.random_int(min=1, max=10)

            # Create a new record
            record = Records(
                employee_id=employee.id,
                start_time=start_time,
                end_time=end_time,
                emails_sent=emails_sent,
                calls_made=calls_made
            )
            db.session.add(record)

    db.session.commit()