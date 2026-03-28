"""
Author: Steven Kolenko
Assignment: #2
Description: Port Scanner — A tool that scans a target machine for open network ports
"""

# Import the required modules (Step ii)
# socket, threading, sqlite3, os, platform, datetime
import socket, threading, sqlite3, os, platform, datetime



# Print Python version and OS name (Step iii)
print("Python Version: " + platform.python_version())
print("Operating System: " + os.name)





# Create the common_ports dictionary (Step iv)
# Add a 1-line comment above it explaining what it stores

# This dictionary maps common network port numbers to the services that typically use them
common_ports = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    143: "IMAP",
    443: "HTTPS",
    3306: "MYSQL",
    3389: "RDP",
    8080: "HTTP-ALT"
}



# Create the NetworkTool parent class (Step v)
# - Constructor: takes target, stores as private self.__target
# - @property getter for target
# - @target.setter with empty string validation
# - Destructor: prints "NetworkTool instance destroyed"
class NetworkTool:
    def __init__(self, target: str):
        self.target = target
    
# Q3: What is the benefit of using @property and @target.setter?
# Your 2-4 sentence answer here... (Part 2, Q3)

# The main benefit is that allows you to access private properties essentially as public properties, but allows for input protection through validation that can be implemented in the setter.
# Not exposing the actual internal variable that is used within the class, is a good practice to prevent accidental misuse.
# When compared to a simple value_set and value_get function, it is much cleaner and simpler, as using it is less like using a function, and more like directly accessing a variable.

    @property
    def target(self):
        return self.__target
    
    @target.setter
    def target(self, value: str):
        if isinstance(value, str) and value.strip() != "": #checks if value is a string, and uses value.strip to check if string is empty or just contains spaces
            self.__target = value
        else:
            print("Error: Target cannot be empty")
        
    def __del__(self):
        print("NetworkTool instance destroyed")

        








# Q1: How does PortScanner reuse code from NetworkTool?
# Your 2-4 sentence answer here... (Part 2, Q1)
"""
PortScanner uses the constructor and deletion message from NetworkTool using super.__init__ and super.()__del__() respectively.
It also intrinsically uses the complex setter and getter from NetworkTool. Reusing code in this manner is an efficient programming technique, as it prevents
the need for repetitive code being used in multiple classes by allowing for one parent class that multiple child classes can inherit from.
"""

# Create the PortScanner child class that inherits from NetworkTool (Step vi)
# - Constructor: call super().__init__(target), initialize self.scan_results = [], self.lock = threading.Lock()
# - Destructor: print "PortScanner instance destroyed", call super().__del__()
class PortScanner(NetworkTool):
    def __init__(self, target: str):
        super().__init__(target)
        self.scan_results = []
        self.lock = threading.Lock()

    def __del__(self):
        print("PortScanner instance destroyed")
        super().__del__()
    

#     - scan_port(self, port):
#     - try-except with socket operations
#     - Create socket, set timeout, connect_ex
#     - Determine Open/Closed status
#     - Look up service name from common_ports (use "Unknown" if not found)
#     - Acquire lock, append (port, status, service_name) tuple, release lock
#     - Close socket in finally block
#     - Catch socket.error, print error message

    def scan_port(self, port):

# Q4: What would happen without try-except here?
# Your 2-4 sentence answer here... (Part 2, Q4)
# The except block allows for error handling, which prevents the program from crashing if there is an error.
# Networks are unpredictable, so errors are relatively common, making the except block extremely important in this function.
# The finally block ensures that the socket closes, regardless of if the code succeeds or fails.

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((self.target, port))

            if result == 0:
                status = "Open"
            else:
                status = "Closed"
            
            service_name = common_ports.get(port, "Unknown")

            with self.lock:
                self.scan_results.append((port, status, service_name))

        except socket.error as error:
            print(f"Error scanning port {port}: {error}")
        finally:
            sock.close()

#
# - get_open_ports(self):
#     - Use list comprehension to return only "Open" results
#
#     
    def get_open_ports(self):
        return [openPort for openPort in self.scan_results if openPort[1] == "Open"]
    
# Q2: Why do we use threading instead of scanning one port at a time?
#     Your 2-4 sentence answer here... (Part 2, Q2)
# Scanning ports is a process that is fairly slow, due to it having to wait for a response from the port.
# The wait can be quite long in the case of a timeout, or a slow network. By threading, we are able to scan multiple ports at once,
# which significantly reduces time to complete all the scans. Scanning one port at a time requires waiting for each individual port
# scan to finish before moving on to the next one, which would take much longer when scanning several ports.

#
# - scan_range(self, start_port, end_port):
#     - Create threads list
#     - Create Thread for each port targeting scan_port
#     - Start all threads (one loop)
#     - Join all threads (separate loop)

    def scan_range(self, start_port, end_port):
        threads = []

        for port in range(start_port, end_port + 1):
            thread = threading.Thread(target=self.scan_port, args=(port,))
            threads.append(thread)

        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()


            




# Create save_results(target, results) function (Step vii)
# - Connect to scan_history.db
# - CREATE TABLE IF NOT EXISTS scans (id, target, port, status, service, scan_date)
# - INSERT each result with datetime.datetime.now()
# - Commit, close
# - Wrap in try-except for sqlite3.Error

def save_results(target, results):
    try:
        conn = sqlite3.connect("scan_history.db")
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target TEXT,
            port INTEGER,
            status TEXT,
            service TEXT,
            scan_date TEXT
        )""")


        for port, status, service, in results:
            cursor.execute("INSERT INTO scans (target, port, status, service, scan_date) VALUES (?, ?, ?, ?, ?)",
            (target, port, status, service, str(datetime.datetime.now()))
            )

        conn.commit()

        conn.close()
    except sqlite3.Error as e:
        print(f"Database error: {e}")





# Create load_past_scans() function (Step viii)
# - Connect to scan_history.db
# - SELECT all from scans
# - Print each row in readable format
# - Handle missing table/db: print "No past scans found."
# - Close connection

def load_past_scans():
    try:
        conn = sqlite3.connect("scan_history.db")
        cursor = conn.cursor()

        cursor.execute("SELECT target, port, status, service, scan_date FROM scans")
        rows = cursor.fetchall()

        if not rows:
            print("No past scans found.")
            return
        
        for target, port, status, service, scan_date in rows:
            print(f"[{scan_date}] {target} : Port {port} ({service}) - {status}")
        
        conn.close()
    except sqlite3.Error:
        print("No past scans found.")








# ============================================================
# MAIN PROGRAM
# ============================================================
if __name__ == "__main__":
    # Get user input with try-except (Step ix)
    # - Target IP (default "127.0.0.1" if empty)
    # - Start port (1-1024)
    # - End port (1-1024, >= start port)
    # - Catch ValueError: "Invalid input. Please enter a valid integer."
    # - Range check: "Port must be between 1 and 1024."
    target = input("Enter Target IP (default: 127.0.0.1): ").strip()
    if target == "":
        target = "127.0.0.1"

    while True:
        try:
            start_port = int(input("Enter start port (1-1024): "))
            if 1 <= start_port <= 1024:
                break
            else:
                print("Port must be between 1 and 1024.")
        except ValueError:
            print("Invalid input. Please enter a valid integer.")

    while True:
        try:
            end_port = int(input("Enter start port (1-1024): "))
            if not (1 <= end_port <= 1024):
                print("Port must be between 1 and 1024.")
            elif end_port < start_port:
                print("End port must be greater than or equal to start port.")
            else:
                break
        except ValueError:
            print("Invalid input. Please enter a valid integer.")


    # After valid input (Step x)
    # - Create PortScanner object
    # - Print "Scanning {target} from port {start} to {end}..."
    # - Call scan_range()
    # - Call get_open_ports() and print results
    # - Print total open ports found
    # - Call save_results()
    # - Ask "Would you like to see past scan history? (yes/no): "
    # - If "yes", call load_past_scans()

    scanner = PortScanner(target)
    print(f"Scanning {target} from port {start_port} to {end_port}")

    scanner.scan_range(start_port, end_port)

    open_ports = scanner.get_open_ports()

    print(f"--- Scan Results for {target} ---")
    for port, status, service in open_ports:
        print(f"Port {port}: {status} ({service})")

    print("------")
    print(f"Total open ports found: {len(open_ports)}")

    save_results(target, scanner.scan_results)

    viewHistory = input("\nWould you like to see past scan history? (yes/no): ").strip().lower()
    if viewHistory == "yes":
        load_past_scans()





# Q5: New Feature Proposal
# Your 2-3 sentence description here... (Part 2, Q5)
"""
The feature I would add would check scan_history.db to look for ports that are open repeatedly across several scans.
It would use a nested if-statement to compare open ports from the current scan with results from previous scans in scan_history.db.
The ports that are commonly open would be displayed to the user for the purpose detecting security vulnerabilities, identifying important services, figuring out unexpected changes, etc.
"""
# Diagram: See diagram_101592125.png in the repository root
