# SecureAuth — Multi-Factor Authentication Demo

SecureAuth is a security-focused Flask web application designed to demonstrate the implementation of modern authentication and application security controls.

The project was developed as a practical cybersecurity portfolio project, with a focus on **authentication security, multi-factor authentication, session management, account protection, rate limiting, and security event logging**.

---

## 🔐 Project Overview

SecureAuth implements a layered authentication process:

**Username & Password → MFA Verification → Protected Dashboard**

The application demonstrates how multiple security controls can work together to protect user accounts and sensitive application resources.

---

## 🎯 Project Objectives

The main objectives of this project were to:

* Implement secure user authentication
* Store passwords using secure password hashing
* Implement account lockout after repeated failed login attempts
* Protect authentication endpoints using rate limiting
* Implement Time-Based One-Time Password (TOTP) multi-factor authentication
* Generate QR codes for MFA enrollment
* Prevent authentication bypass
* Secure user sessions
* Protect authenticated routes
* Record security events in an audit log
* Perform practical security testing against the implemented controls

---

## 🛡️ Security Features

### 1. Password Authentication

Users authenticate using a username and password.

Passwords are never stored in plaintext. Passwords are securely hashed using Werkzeug's password hashing functionality before being stored in the database.

### 2. Account Lockout

The application tracks failed authentication attempts.

After **5 consecutive failed password attempts**, the account is automatically locked.

This helps protect against repeated password-guessing attempts.

### 3. Rate Limiting

Authentication endpoints are protected using Flask-Limiter.

The login endpoint is limited to:

**10 requests per minute**

The MFA verification endpoint is limited to:

**5 requests per minute**

This provides an additional layer of protection against automated authentication attempts.

### 4. Multi-Factor Authentication

SecureAuth implements TOTP-based MFA using PyOTP.

Users can enroll their authenticator application by scanning a generated QR code.

After password authentication, users with MFA enabled must provide a valid six-digit TOTP code before accessing protected resources.

### 5. MFA Bypass Protection

Users who have successfully entered their password but have not completed MFA are prevented from accessing protected routes.

Attempting to access the dashboard before completing MFA results in an unauthorized-access event.

### 6. Session Security

The application uses secure session configuration including:

* HTTPOnly session cookies
* SameSite cookie protection
* Configurable session lifetime
* Session clearing during logout
* MFA verification state tracking

### 7. Security Event Logging

Security-relevant events are recorded in:

`secureauth_security.log`

The application records events including:

* `LOGIN_FAILURE`
* `ACCOUNT_LOCKED`
* `PASSWORD_AUTH_SUCCESS`
* `MFA_FAILURE`
* `MFA_SUCCESS`
* `UNAUTHORIZED_ACCESS`
* `LOGOUT`

These events provide an audit trail that can be used for security monitoring and investigation.

---

## 🧪 Security Testing

The implemented security controls were tested manually during development.

| Security Test                     | Expected Result                | Result   |
| --------------------------------- | ------------------------------ | -------- |
| Incorrect password                | Authentication rejected        | ✅ Passed |
| Five failed password attempts     | Account locked                 | ✅ Passed |
| Account lockout logging           | `ACCOUNT_LOCKED` recorded      | ✅ Passed |
| Login rate limiting               | Excess requests rejected       | ✅ Passed |
| Correct password with MFA enabled | MFA verification required      | ✅ Passed |
| Invalid MFA code                  | Authentication rejected        | ✅ Passed |
| MFA failure logging               | `MFA_FAILURE` recorded         | ✅ Passed |
| Valid MFA code                    | Dashboard access granted       | ✅ Passed |
| MFA success logging               | `MFA_SUCCESS` recorded         | ✅ Passed |
| Dashboard access before MFA       | Access denied                  | ✅ Passed |
| Unauthorized access logging       | `UNAUTHORIZED_ACCESS` recorded | ✅ Passed |
| Logout                            | Session terminated             | ✅ Passed |
| Dashboard access after logout     | Access denied                  | ✅ Passed |
| Logout logging                    | `LOGOUT` recorded              | ✅ Passed |

---

## 🏗️ Technology Stack

### Backend

* Python
* Flask
* Flask-SQLAlchemy
* Flask-Limiter

### Security

* Werkzeug password hashing
* PyOTP
* TOTP-based MFA
* Session security
* Account lockout
* Rate limiting
* Security event logging

### Database

* SQLite
* SQLAlchemy ORM

### Frontend

* HTML5
* CSS3
* Jinja2 templates

### Development Tools

* Visual Studio Code
* Git
* GitHub
* GitHub Desktop

---

## 📁 Project Structure

```text
MFA Demo App/
│
├── app.py
├── config.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes.py
│   └── security.py
│
├── templates/
│   ├── login.html
│   ├── register.html
│   └── mfa_verify.html
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│
├── screenshots/
│
└── tests/
```

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/MrsWealth20/MFA-Demo-App.git
cd MFA-Demo-App
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the application

```bash
python app.py
```

The application will be available locally at:

```text
http://127.0.0.1:5000
```

---

## 🔑 Authentication Flow

```text
User
 │
 ▼
Login
 │
 ├── Invalid credentials
 │       │
 │       └── LOGIN_FAILURE
 │
 ▼
Password Authentication
 │
 ├── MFA disabled ───────► Dashboard
 │
 └── MFA enabled
          │
          ▼
     MFA Verification
          │
          ├── Invalid code
          │       │
          │       └── MFA_FAILURE
          │
          └── Valid code
                  │
                  └── MFA_SUCCESS
                          │
                          ▼
                      Dashboard
```

---

## 📊 Security Audit Trail

Example security events generated by the application:

```text
EVENT=LOGIN_FAILURE | USER=Tshepho

EVENT=ACCOUNT_LOCKED | USER=Tshepho | DETAILS=5 failed login attempts

EVENT=PASSWORD_AUTH_SUCCESS | USER=Tshepho

EVENT=MFA_FAILURE | USER=Tshepho

EVENT=MFA_SUCCESS | USER=Tshepho

EVENT=UNAUTHORIZED_ACCESS | USER=Tshepho | DETAILS=Attempted access to /dashboard before MFA verification

EVENT=LOGOUT | USER=Tshepho
```

The audit trail demonstrates how authentication and authorization events can be captured for security monitoring and investigation.

---

## 🔎 Security Considerations

This project is intended as an educational cybersecurity demonstration and local security lab.

For production deployment, additional controls would be recommended, including:

* HTTPS/TLS
* Secure production secret management
* CSRF protection
* Stronger password policies
* Persistent rate-limit storage
* Centralized logging
* Log integrity protection
* Account recovery controls
* MFA recovery procedures
* Security headers
* Production-grade database configuration
* Automated security testing
* Monitoring and alerting

---

## 🚀 Future Improvements

Potential future enhancements include:

* Email-based account recovery
* Password reset functionality
* Role-based access control
* Administrative security dashboard
* Security event visualization
* Persistent Redis-based rate limiting
* Automated unit and integration tests
* CSRF protection
* Security headers
* Simulated biometric authentication
* Containerized deployment
* CI/CD security checks
* Integration with a SIEM platform

---

## 🎓 Cybersecurity Skills Demonstrated

This project demonstrates practical experience with:

* Authentication and authorization
* Password security
* Multi-factor authentication
* TOTP
* Account lockout controls
* Rate limiting
* Session management
* Security logging
* Audit trails
* Access control
* Security testing
* Flask web application security
* Database integration
* Secure coding practices
* Git/GitHub project management

---

## 📌 Project Status

**Status: Completed**

SecureAuth was developed as a hands-on cybersecurity project to demonstrate the design, implementation, testing, and documentation of layered authentication security controls.

---

## ⚠️ Disclaimer

SecureAuth is an educational cybersecurity project intended for authorized testing and learning purposes.

It should not be considered a production-ready authentication system without additional security hardening, testing, and review.
