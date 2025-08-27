## 📄 Simple Share App
Simple Share App is a web application designed for easily sharing text and files. It's built to allow users on the same network to quickly exchange content by scanning a QR code or accessing a simple link.

The app requires no sign-up or login process, making it possible to upload and share content instantly.

### ✨ Key Features
Text Sharing: Write and share text freely.

File Upload: Easily upload files up to 5MB using drag-and-drop or a standard file selection dialog.

Infinite Scroll: The main page automatically loads past content as you scroll down, providing a seamless browsing experience.

QR Code Sharing: Access the app quickly on mobile devices by scanning a QR code that displays the server's IP address.

Simple Deletion: Uploaded content can be instantly deleted from the list.

Security: HTML escaping is implemented to prevent Cross-Site Scripting (XSS) attacks.

## 💻 Technology Stack
Backend: Flask (Python)

Database: SQLite

Frontend: HTML, CSS (Tailwind CSS), JavaScript (jQuery)

## 🚀 How to Run the Project
Install Required Libraries:
Install the project's dependencies.
```
pip install -r requirements.txt
```

## Run the Application:
```
python run.py
```

## Access the App:
Once the application is running, open a web browser and navigate to the address shown in the terminal, such as http://0.0.0.0:5000.

To access the app from another device on the same network, scan the QR code on the /qr page or navigate to http://[SERVER_LOCAL_IP]:5000.

## 📂 Project Structure
```
.
├── app/
│   ├── static/               # CSS, JS, and other static files
│   │   ├── css/
│   │   └── js/
│   ├── templates/            # HTML template files
│   ├── __init__.py           # Flask app initialization and configuration
│   ├── database.py           # SQLite database setup
│   └── routes.py             # Routing and business logic
├── instance/                 # Folder for uploaded files (automatically created)
├── run.py                    # Application startup script
├── requirements.txt          # Python dependency list
└── README.md                 # Project description
```

