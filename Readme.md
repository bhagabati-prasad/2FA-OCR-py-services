# API Endpoints:

Document Info Extract:

- http://127.0.0.1:5000/api/doc/extract/aadhaar-front
- http://127.0.0.1:5000/api/doc/extract/aadhaar-back
- http://127.0.0.1:5000/api/doc/extract/pan
- http://127.0.0.1:5000/api/doc/extract/payslip
- http://127.0.0.1:5000/api/doc/extract/account-statement
- http://127.0.0.1:5000/api/doc/extract/vehicle-quotation

Biometric Auths:

- http://127.0.0.1:5000/api/auth/face/encode
- http://127.0.0.1:5000/api/auth/face/match
- http://127.0.0.1:5000/api/auth/fingerprint/encode
- http://127.0.0.1:5000/api/auth/fingerprint/match
- http://127.0.0.1:5000/api/auth/iris/encode
- http://127.0.0.1:5000/api/auth/iris/match

Cheque Scan:

- http://127.0.0.1:5000/api/cheque/extract

# Libraries used:

---

- traceback: Add for detailed error info.

Cmake in Linux
sudo apt-get update
sudo apt-get install cmake
pip install dlib

# Basic instructions:

---

- Use `def __method_name()` or `__variable_name` to make it private. SO, it'll be accessed only in same file, not outside of the file.
