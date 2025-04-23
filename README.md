# Cipher

Cipher is a social media prototype designed to help users maintain control over their images and protect themselves from sextortion and cyberbullying. The platform empowers users by giving them full control of their shared images, ensuring a safer and more secure online experience.

## Video Demo

[![Watch the Video](https://img.youtube.com/vi/1oI84U_IadVh9uUoqZU2E2HzTyBRkHUjR/0.jpg)](https://drive.google.com/file/d/1oI84U_IadVh9uUoqZU2E2HzTyBRkHUjR/view?ts=6687f69a)

Click the image above to watch the video demonstration.

## Features

- **Image Control**: Users retain full control over their shared photos, deciding who can access and share them further.
- **Digital Footprint Tracking**: View the digital footprint of your shared images for complete transparency.
- **Screenshot Prevention**: Detects when a phone camera is pointed at the screen while viewing an image and automatically blurs the image to prevent screenshots.
- **Privacy and Security**: Ensures that shared content remains secure and protected from misuse.

## How It Works

1. **Share Images Securely**: Share images with specific people while keeping control over who can access or share them.
2. **Track Footprints**: Keep track of where your images are being accessed and shared.
3. **Screenshot Detection**: If a phone camera is detected while viewing an image, the platform blurs the image to prevent unauthorized screenshots.

## Why Cipher?

Cipher is built to provide a safer online environment for sharing images. By leveraging innovative technology, it ensures that users can share their memories without fear of misuse or exploitation.


## Project Structure

```
cipher/
│
├── app.py                # Application factory and extensions
├── run.py                # Entry point to run the app
├── models.py             # Database models
├── routes.py             # All Flask routes (views)
├── forms.py              # WTForms classes
├── utils.py              # Utility functions
├── events.py             # (If using Flask-SocketIO events)
├── templates/            # Jinja2 HTML templates
├── static/               # Static files (CSS, JS, images)
└── README.md
```

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd cipher
```

### 2. Create and Activate a Virtual Environment

```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
python run.py
```

The app will be available at [http://localhost:5000](http://localhost:5000).

---

## Usage

- Register a new user at `/register`
- Log in at `/login`
- Use the navigation links to send images, view your packages, manage sharing, and more

---

## Notes

- All route references in templates use the `main.` prefix, e.g. `url_for('main.home')`
- The database (`site.db`) is created automatically on first run
- To reset the database, delete `site.db` and restart the app

---

## Customization

- Add your own CSS in the `static/` folder
- Modify templates in the `templates/` folder
- Add new routes or models as needed in their respective files

---

## License

MIT (or your chosen license)
