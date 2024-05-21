import psycopg2
from config import host, user, password, db_name

try: 
    connection  = psycopg2.connect(
        host=host,
        user=user,
        password=password,
        database=db_name
    )
    
    connection.autocommit = True

    with connection.cursor() as cursor:
        create_tables_queries = [
            """
            CREATE TABLE IF NOT EXISTS InsuranceCompanies (
                insurance_company_id SERIAL PRIMARY KEY,
                company_name VARCHAR(100),
                address VARCHAR(255),
                INN VARCHAR(20),
                checking_account VARCHAR(30),
                BIK VARCHAR(20)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS Services (
                service_id SERIAL PRIMARY KEY,
                service_name VARCHAR(100),
                cost DECIMAL(10, 2),
                execution_time INT,
                average_deviation DECIMAL(5, 2)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS Patients (
                patient_id SERIAL PRIMARY KEY,
                username VARCHAR(50),
                password VARCHAR(50),
                full_name VARCHAR(100),
                date_of_birth DATE,   
                passport_number VARCHAR(20),
                phone VARCHAR(20),
                email VARCHAR(100),
                insurance_policy_number VARCHAR(20),
                insurance_company_name VARCHAR(50),
                insurance_policy_type VARCHAR(50),
                insurance_company_id INT,
                FOREIGN KEY (insurance_company_id) REFERENCES InsuranceCompanies(insurance_company_id)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS Orders (
                order_id SERIAL PRIMARY KEY,
                order_number VARCHAR(100),
                patient_id INT,
                order_name VARCHAR(100), 
                order_date DATE,
                status VARCHAR(50),
                FOREIGN KEY (patient_id) REFERENCES Patients(patient_id)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS OrderServices (
                order_service_id SERIAL PRIMARY KEY,
                order_id INT,
                service_id INT,
                service_status VARCHAR(50),
                service_completion_time INT,
                FOREIGN KEY (order_id) REFERENCES Orders(order_id),
                FOREIGN KEY (service_id) REFERENCES Services(service_id)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS Analyzers (
                analyzer_id SERIAL PRIMARY KEY,
                analyzer_name VARCHAR(100)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS LaboratoryStaff (
                staff_id SERIAL PRIMARY KEY,
                username VARCHAR(50),
                password VARCHAR(50),
                full_name VARCHAR(100),
                last_login_date TIMESTAMP,
                services_provided VARCHAR(255),
                role VARCHAR(100)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS Accountants (
                accountant_id SERIAL PRIMARY KEY,
                username VARCHAR(50),
                password VARCHAR(50),
                full_name VARCHAR(100),
                last_login_date TIMESTAMP,
                issued_invoices VARCHAR(255)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS Administrators (
                admin_id SERIAL PRIMARY KEY,
                username VARCHAR(50),
                password VARCHAR(50)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS PerformedServices (
                performed_service_id SERIAL PRIMARY KEY,
                order_service_id INT,
                analyzer_id INT,
                performer_id INT,
                service_date TIMESTAMP,
                FOREIGN KEY (order_service_id) REFERENCES OrderServices(order_service_id),
                FOREIGN KEY (analyzer_id) REFERENCES Analyzers(analyzer_id),
                FOREIGN KEY (performer_id) REFERENCES LaboratoryStaff(staff_id)
            );
            """
        ]
        for query in create_tables_queries:
            cursor.execute(query)
        print("[INFO] All tables were created successfully")
        
        insert_laboratory_staff_query = """
            INSERT INTO LaboratoryStaff (username, password, full_name, last_login_date, services_provided, role) 
            VALUES 
            ('a', 'a', 'Lab Technician One', '2024-05-18 10:00:00', 'Service A, Service B', 'Lab Technician')
        """

        insert_patients_query = """
            INSERT INTO Patients (full_name, date_of_birth, passport_number, phone, email, insurance_policy_number, insurance_policy_type, insurance_company_name)
            VALUES 
            ('alex', '1987-09-20', '33422313', '+77478815383', 'alex@mail.ru', '123123', 'omb', 'olgrgaf')
        """

        cursor.execute(insert_laboratory_staff_query)
        cursor.execute(insert_patients_query)
        print("[INFO] LaboratoryStaff table was filled with sample data")

except Exception as _ex:
    print("Error while working with PostgreSQL: ", _ex)

finally: 
    if connection:
        connection.close()
        print("[INFO] Connection closed")
