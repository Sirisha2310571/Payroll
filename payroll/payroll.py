import sqlite3

# Connect to the SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('payroll_system.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM Attendance")
print(cursor.fetchall())
conn.close()

# SQL statements to create the tables
"""
cursor.execute('''

    CREATE TABLE IF NOT EXISTS Users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
);
''')

users = [
    ('Saruleka', 'saru'),
    ('Sirisha', 'siri'),
    ('Swetha', 'swe')
]

cursor.executemany('''
INSERT INTO Users (username, password)
VALUES (?, ?)
''', users)

cursor.execute('''
CREATE TABLE Employee (
    employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    phone_number TEXT,
    job_title TEXT,
    department TEXT,
    hire_date DATE,
    salary REAL,
    status TEXT DEFAULT 'Active'
''');


cursor.execute('''
    CREATE TABLE Attendance (
    attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER,
    date DATE NOT NULL,
    check_in_time TIME,
    check_out_time TIME,
    status TEXT DEFAULT 'Present',
    FOREIGN KEY (employee_id) REFERENCES Employee(employee_id))
''');

cursor.execute('''
    CREATE TABLE Payroll (
    payroll_id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER,
    pay_period_start DATE,
    pay_period_end DATE,
    base_salary REAL,
    deductions REAL,
    bonuses REAL,
    total_salary REAL,
    generated_on DATE DEFAULT CURRENT_DATE,
    FOREIGN KEY (employee_id) REFERENCES Employee(employee_id)
);
''')

cursor.execute('''CREATE TABLE Leave (
    leave_id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER,
    leave_type TEXT,
    start_date DATE,
    end_date DATE,
    status TEXT DEFAULT 'Pending',
    FOREIGN KEY (employee_id) REFERENCES Employee(employee_id)
);
''')

cursor.execute('''
    CREATE TABLE Deductions (
    deduction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER,
    deduction_type TEXT,
    amount REAL,
    date_applied DATE DEFAULT CURRENT_DATE,
    FOREIGN KEY (employee_id) REFERENCES Employee(employee_id)
);
''')
# Insert values into the Employee table
employees = [
    ('Karthick', 'Natrajan', 'karthick@gmail.com', '8122786469', 'Data Analyst', 'Analytics', '2023-03-10', 60000, 'Active'),
    ('Satheesh', 'Kumar', 'satheesh@gmail.com', '9894197799', 'Software Developer', 'IT', '2022-11-25', 75000, 'Active'),
    ('Sabiha', 'Mary', 'sabiha@gmail.com', '9994274559', 'Product Manager', 'Product', '2021-08-15', 90000, 'Active')
]
cursor.executemany('''INSERT INTO Employee (first_name, last_name, email, phone_number, job_title, department, hire_date, salary, status) 
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', employees)

# Insert values into the Attendance table
attendance_records = [
    (1, '2024-11-01', '09:00:00', '17:00:00', 'Present'),
    (1, '2024-11-02', '09:00:00', '17:00:00', 'Present'),
    (2, '2024-11-01', '09:15:00', '17:10:00', 'Late'),
    (3, '2024-11-01', '08:45:00', '16:45:00', 'Present')
]
cursor.executemany('''INSERT INTO Attendance (employee_id, date, check_in_time, check_out_time, status) 
                      VALUES (?, ?, ?, ?, ?)''', attendance_records)

# Insert values into the Payroll table
payroll_records = [
    (1, '2024-10-01', '2024-10-31', 60000, 500, 2000, 61500),
    (2, '2024-10-01', '2024-10-31', 75000, 800, 1500, 75700),
    (3, '2024-10-01', '2024-10-31', 90000, 1200, 2500, 91300)
]
cursor.executemany('''INSERT INTO Payroll (employee_id, pay_period_start, pay_period_end, base_salary, deductions, bonuses, total_salary) 
                      VALUES (?, ?, ?, ?, ?, ?, ?)''', payroll_records)

# Insert values into the Leave table
leave_records = [
    (1, 'Vacation', '2024-12-01', '2024-12-05', 'Approved'),
    (2, 'Sick', '2024-11-10', '2024-11-12', 'Approved'),
    (3, 'Maternity', '2024-09-01', '2024-12-01', 'Approved')
]
cursor.executemany('''INSERT INTO Leave (employee_id, leave_type, start_date, end_date, status) 
                      VALUES (?, ?, ?, ?, ?)''', leave_records)

# Insert values into the Deductions table
deductions = [
    (1, 'Health Insurance', 500),
    (2, 'Pension', 800),
    (3, 'Health Insurance', 1200)
]
cursor.executemany('''INSERT INTO Deductions (employee_id, deduction_type, amount) 
                      VALUES (?, ?, ?)''', deductions)

cursor.execute('''

CREATE TRIGGER calculate_total_salary
AFTER INSERT ON Payroll
FOR EACH ROW
BEGIN
    UPDATE Payroll
    SET total_salary = NEW.base_salary - NEW.deductions + NEW.bonuses
    WHERE payroll_id = NEW.payroll_id;
END;''')

cursor.execute('''
    CREATE TABLE ActivityLog (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    activity_type TEXT,
    description TEXT,
    log_date DATE DEFAULT CURRENT_DATE,
    employee_id INTEGER,
    FOREIGN KEY (employee_id) REFERENCES Employee(employee_id))
''');

cursor.execute('''
CREATE TRIGGER log_attendance
AFTER INSERT ON Attendance
FOR EACH ROW
BEGIN
    INSERT INTO ActivityLog (activity_type, description, employee_id)
    VALUES (
        'Attendance',
        (SELECT first_name || ' ' || last_name || ' checked in' FROM Employee WHERE employee_id = NEW.employee_id),
        NEW.employee_id
    );
END;
''')

# Commit changes and close the connection
conn.commit()
conn.close() 

print("Database and tables created successfully.")"""
