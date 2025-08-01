# 🎉 EpicEvent 🎉
**EpicEvent** is a CLI management application for an event planning company.  
It allows you to:  
- Create collaborators divided into three departments (management, sales, and event support)  
- Create clients  
- Create contracts  
- And finally, create events follow-up records.

It uses the user's role to define the actions they are allowed to perform in the application.

---

## 🚀 Main Features

- Management of events linked to client contracts  
- User authentication  
- Custom ORM based on SQLAlchemy without a framework  
- Management of sessions, permissions, and database rollback  
- Automated tests with `pytest` and `pexpect`

---

## 🛠️ Technologies Used

- **Python 3.12+**
- **SQLAlchemy** (ORM)
- **SQLite**
- **Pexpect** (UI tests)
- **Pytest** (unit, functional and integration tests)
- **Integrated Logging** (with `logger` per module and Sentry)

---


## 🧱 Architecture
```bash
Repository/
    ├── epic_event/             # Main code of the application
    │   ├── controllers/        # Coordination logic between models and views
    │   ├── models/             # ORM SQLAlchemy 
    │   ├── views/              # Presentation layer  
    │   ├── tests/              # Tests Selenium & Pytest
    │   ├── permission.py       # Management of permissions and roles
    │   └── settings.py         # Configuration parameters (DB, constants, logger)
    ├── main.py                 # Entry point of the application
    ├── README.md
    ├── requirements.txt
    └── Schémas_BDD_Epic_Event.pdf  # schemas of the database
```

---
### 1. Clone the Repository

First, open the command prompt in the folder where you want to drop the clone.

clone this repository to your local machine. 

```bash
git clone https://github.com/Mikael2983/OC-P12_Develop_secure_back-end_architecture_with_Python_and_SQL.git
```
Then navigate inside the created folder

```bash
cd OC-P12_Develop_secure_back-end_architecture_with_Python_and_SQL
```

### 2. Create Virtual Environment

To create virtual environment, install virtualenv package of python and activate it by following command on terminal:

```bash
python -m venv .venv
```
for windows:
```bash
.venv\Scripts\activate
```
for Unix/MacOS :
```bash
source .venv/bin/acivate
```

### 3. Requirements

To install required python packages, copy requirements.txt file and then run following command on terminal:

```bash
pip install -r requirements.txt
```
### 4. Initialize Database

EpicEvent already contains the necessary data for tests or demos.

Depending on the server launch command, the corresponding data will be loaded.

### 5. Start Cli application

To see the data used for Pytest and Pexpect tests, 

On the terminal enter following command to start the server::
```bash
python main.py test
```

To discover the application's features, enter following command to start the application:
```bash
python main.py demo
```

For your own usage, enter following command to start the application:

```bash
python main.py
```


### 6. Connexion

To log in to a SUPERUSER account,
- with test database:

    Fill in the name: Admin and password: mypassword

    All test database accounts use the same password


- with others databases:
    
    Fill in the name: Admin User and password: adminpass.

    All demo database accounts use the password first name+pass.

    e.g: Alice Martin use alicepass as password

### 8. Tests

all the tests as well as the server intended for them are already configured

all you need is to enter the pytest command on the terminal.

```bash
pytest
```