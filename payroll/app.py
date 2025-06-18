from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Secret key for session management (if needed)
app.secret_key = 'your_secret_key'

# Database connection function
def get_db_connection():
    conn = sqlite3.connect('payroll_system.db')  # Connect to your database
    conn.row_factory = sqlite3.Row  # This ensures that the rows returned are dictionaries
    return conn

@app.route("/")
def hello_world():
    return render_template("login.html")
# Login route

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get the form data (username and password)
        username = request.form['username'].strip()
        password = request.form['password'].strip()

        # Connect to the database and check if the user exists with the provided username and hashed password
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM Users WHERE username = ? AND password = ?', (username, password)).fetchone()

        conn.execute('select * from Users')
        conn.close()
      
        if user:
            # User found, login successful
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
      # Redirect to the dashboard or another page
        else:
            # Invalid username or password
            flash('Invalid username or password', 'danger')

    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    conn = get_db_connection()
    cursor=conn.cursor()

    query_conditions = []
    params = []

    cursor.execute("SELECT * FROM leave WHERE status = 'Pending' ORDER BY leave_id DESC")
    leave_requests = cursor.fetchall()

    # Build the WHERE clause dynamically
    where_clause = " AND ".join(query_conditions) if query_conditions else "1=1"

    # Query to get total salary disbursed
    total_salary_disbursed_query = f"""
    SELECT SUM(total_salary) 
    FROM Payroll 
    JOIN Employee ON Payroll.employee_id = Employee.employee_id
    WHERE {where_clause}
    """
    total_salary_disbursed = conn.execute(total_salary_disbursed_query, params).fetchone()[0]

    # If no data is found, set to 0
    total_salary_disbursed = total_salary_disbursed if total_salary_disbursed else 0.0

    # Query to get total employees
    total_employees_query = f"SELECT COUNT(*) FROM Employee WHERE {where_clause}"
    total_employees = conn.execute(total_employees_query, params).fetchone()[0]

    # Query to get attendance today
    attendance_today_query = f"""
    SELECT COUNT(*) 
    FROM Attendance 
    WHERE date = date('now')
    """
    attendance_today = conn.execute(attendance_today_query).fetchone()[0]

    # Query for recent activity (You can adjust this query based on your activity logs)
    recent_activity_query = """
    SELECT activity_type, log_date FROM ActivityLog ORDER BY log_date DESC LIMIT 5
    """
    recent_activity = conn.execute(recent_activity_query).fetchall()  

    conn.close()

    # Render the dashboard template with data
    return render_template(
        'dashboard.html',
        
        total_salary_disbursed=total_salary_disbursed,
        total_employees=total_employees,
        attendance_today=attendance_today,
        recent_activity=recent_activity,
        leave_requests=leave_requests
    )


# Route for Employee Management Dashboard
@app.route('/employee')
def employee():
    conn = get_db_connection()
    employees = conn.execute("SELECT * FROM Employee").fetchall()
    print(employees)
    conn.close()
    return render_template('employee.html', employees=employees)


@app.route('/add_employee', methods=['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        job_title = request.form['job_title']
        department = request.form['department']
        hire_date = request.form['hire_date']

        conn = get_db_connection()
        conn.execute("INSERT INTO Employee (first_name, last_name, email, job_title, department, hire_date) VALUES (?, ?, ?, ?, ?, ?)",
                     (first_name, last_name, email, job_title, department, hire_date))
        conn.commit()
        conn.close()
        return redirect(url_for('employee'))
    return render_template('add_employee.html')

@app.route('/view_employee', methods=['GET', 'POST'])
def view_employee():
    search_query = request.args.get('search', '')  # Get the search term from URL parameters
    conn = get_db_connection()
    
    # Check if there's a search term and modify the query accordingly
    if search_query:
        # Search by first name, last name, or job title
        employees = conn.execute(
            "SELECT * FROM Employee WHERE first_name LIKE ? OR last_name LIKE ? OR job_title LIKE ?",
            ('%' + search_query + '%', '%' + search_query + '%', '%' + search_query + '%')
        ).fetchall()
    else:
        # No search term, so return all employees
        employees = conn.execute("SELECT * FROM Employee").fetchall()

    conn.close()
    
    # Render the employee page and pass the employees data
    return render_template('add_employee.html', employees=employees, search_query=search_query)

@app.route('/manage_employees', methods=['GET', 'POST'])
def manage_employees():
    conn = get_db_connection()
    employees = conn.execute("SELECT * FROM Employee").fetchall()

    if request.method == 'POST':
        employee_id = request.form.get('employee_id')

        if 'update_employee' in request.form:
            # Update employee details
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            email = request.form.get('email')
            job_title = request.form.get('job_title')
            department = request.form.get('department')

            conn.execute(
                "UPDATE Employee SET first_name = ?, last_name = ?, email = ?, job_title = ?, department = ? WHERE employee_id = ?",
                (first_name, last_name, email, job_title, department, employee_id)
            )
            conn.commit()
            flash("Employee details updated successfully.", "success")

        elif 'delete_employee' in request.form:
            # Delete the employee
            conn.execute("DELETE FROM Employee WHERE employee_id = ?", (employee_id,))
            conn.commit()
            flash("Employee deleted successfully.", "success")

    conn.close()
    return render_template('update.html', employees=employees)


class PayrollStrategy:
    def calculate(self, base_salary, bonuses, deductions, unpaid_leave_deduction):
        pass

class BasicPayrollStrategy(PayrollStrategy):
    def calculate(self, base_salary, bonuses, deductions, unpaid_leave_deduction):
        return base_salary + bonuses - deductions - (unpaid_leave_deduction if unpaid_leave_deduction else 0)

class AdvancedPayrollStrategy(PayrollStrategy):
    def calculate(self, base_salary, bonuses, deductions, unpaid_leave_deduction):
        # This could be a more complex calculation (e.g., including other benefits or taxes)
        return base_salary + bonuses - deductions - (unpaid_leave_deduction if unpaid_leave_deduction else 0)

class PayrollContext:
    def __init__(self, strategy: PayrollStrategy):
        self.strategy = strategy
    
    def set_strategy(self, strategy: PayrollStrategy):
        self.strategy = strategy

    def calculate_salary(self, base_salary, bonuses, deductions, unpaid_leave_deduction):
        return self.strategy.calculate(base_salary, bonuses, deductions, unpaid_leave_deduction)

@app.route('/payroll', methods=['GET', 'POST'])
def payroll():
    conn = sqlite3.connect('payroll_system.db')
    cursor = conn.cursor()

    # Add Payroll functionality
    if request.method == 'POST':
        employee_id = request.form['employee_id']
        pay_period_start = request.form['pay_period_start']
        pay_period_end = request.form['pay_period_end']
        bonuses = float(request.form['bonuses'])

        # Fetch employee details
        cursor.execute('SELECT base_salary FROM Payroll WHERE employee_id = ?', (employee_id,))
        employee = cursor.fetchone()
        if not employee:
            flash('Employee ID does not exist!', 'error')
            return redirect(url_for('payroll'))

        base_salary = employee[0]

        # Define default deductions and unpaid leave deduction (you can fetch these from the database)
        deductions = 100  # example
        unpaid_leave_deduction = 50  # example

        # Using Strategy Pattern for payroll calculation
        context = PayrollContext(BasicPayrollStrategy())  # You can switch to AdvancedPayrollStrategy if needed
        total_salary = context.calculate_salary(base_salary, bonuses, deductions, unpaid_leave_deduction)

        # Check if payroll already exists
        cursor.execute('''
            SELECT * FROM Payroll WHERE employee_id = ? AND pay_period_start = ? AND pay_period_end = ?
        ''', (employee_id, pay_period_start, pay_period_end))
        existing_payroll = cursor.fetchone()

        if existing_payroll:
            flash('Payroll for this period already exists for the employee.', 'error')
        else:
            cursor.execute('''
                INSERT INTO Payroll (employee_id, pay_period_start, pay_period_end, base_salary, bonuses, deductions, total_salary, generated_on)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (employee_id, pay_period_start, pay_period_end, base_salary, bonuses, deductions, total_salary, datetime.now().strftime('%Y-%m-%d')))
            conn.commit()
            flash('Payroll added successfully!', 'success')

    # View Payroll functionality
    cursor.execute('''
        SELECT p.payroll_id, e.first_name, e.last_name, p.base_salary, p.deductions,p.bonuses, p.total_salary, p.pay_period_start, p.pay_period_end, p.generated_on
        FROM Payroll p
        JOIN Employee e ON p.employee_id = e.employee_id
        ORDER BY p.generated_on DESC
    ''')
    payroll_records = cursor.fetchall()

    conn.close()

    return render_template('payroll.html', payroll_records=payroll_records)


class DatabaseConnection:
    _instance = None

    def __init__(self):
        if DatabaseConnection._instance is None:
            self.conn = sqlite3.connect('payroll_system.db', check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            DatabaseConnection._instance = self

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = DatabaseConnection()
        return cls._instance

    def get_cursor(self):
        return self.conn.cursor()

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()

db_instance = DatabaseConnection.get_instance()

class LeaveState:
    def handle_status(self):
        pass

class ApprovedState(LeaveState):
    def handle_status(self):
        return "Approved"

class PendingState(LeaveState):
    def handle_status(self):
        return "Pending"

class DeclinedState(LeaveState):
    def handle_status(self):
        return "Declined"

# Context class to manage leave state
class LeaveRequest:
    def __init__(self, state: LeaveState):
        self._state = state

    def set_state(self, state: LeaveState):
        self._state = state

    def get_status(self):
        return self._state.handle_status()


class Observer:
    def update(self, message):
        pass

class AttendanceObserver(Observer):
    def update(self, message):
        flash(message)

class AttendanceSubject:
    def __init__(self):
        self._observers = []

    def add_observer(self, observer: Observer):
        self._observers.append(observer)

    def notify_observers(self, message):
        for observer in self._observers:
            observer.update(message)

attendance_subject = AttendanceSubject()
attendance_observer = AttendanceObserver()
attendance_subject.add_observer(attendance_observer)

class AttendanceReport:
    def generate_report(self):
        pass

class MonthlyAttendanceReport(AttendanceReport):
    def __init__(self, data):
        self.data = data

    def generate_report(self):
        # Generate monthly attendance report using self.data
        return self.data

@app.route('/attendance', methods=['GET', 'POST'])
def attendance():
    cursor = db_instance.get_cursor()
    
    if request.method == 'POST':
        if 'add_attendance' in request.form:
            employee_id = request.form['employee_id']
            date = request.form['date']
            status = request.form['status']
            check_in_time = request.form['check_in_time']
            check_out_time = request.form['check_out_time']

            # Check for duplicate attendance record
            cursor.execute('''SELECT * FROM Attendance WHERE employee_id = ? AND date = ?''', (employee_id, date))
            existing_record = cursor.fetchone()
            if existing_record:
                flash("Error: Attendance record already exists for this employee on the selected date.", "error")
            else:
                cursor.execute('''INSERT INTO Attendance (employee_id, date, check_in_time, check_out_time, status)
                                  VALUES (?, ?, ?, ?, ?)''', 
                               (employee_id, date, check_in_time, check_out_time, status))
                db_instance.commit()
                flash("Attendance record added successfully.", "success")

        elif 'add_leave' in request.form:
            employee_id = request.form['employee_id']
            leave_type = request.form['leave_type']
            start_date = request.form['start_date']
            end_date = request.form['end_date']

            cursor.execute('''INSERT INTO Leave (employee_id, leave_type, start_date, end_date)
                              VALUES (?, ?, ?, ?)''', 
                           (employee_id, leave_type, start_date, end_date))
            db_instance.commit()
            flash("Leave request submitted successfully.", "success")

    cursor.execute('''SELECT a.*, e.first_name, e.last_name FROM Attendance a 
                      JOIN Employee e ON a.employee_id = e.employee_id''')
    attendance_records = cursor.fetchall()

    cursor.execute('''SELECT l.*, e.first_name, e.last_name FROM Leave l 
                      JOIN Employee e ON l.employee_id = e.employee_id''')
    leave_records = cursor.fetchall()

    return render_template('attendance.html', attendance_records=attendance_records, leave_records=leave_records)

# Update Leave Status
@app.route('/leave_status', methods=['POST'])
def leave_status():
    leave_id = request.form['leave_id']
    status = request.form['status']

    conn = get_db_connection()
    cursor = conn.cursor()

    # Update the leave status based on leave_id
    cursor.execute("UPDATE Leave SET status = ? WHERE leave_id = ?", (status, leave_id))
    conn.commit()
    conn.close()

    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)