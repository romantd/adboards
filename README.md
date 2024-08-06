# AdBoards

AdBoards is a web application for posting and browsing classified ads. Users can create profiles, post ads, and search for ads in various categories.

## Features

- User authentication (sign up, login, logout)
- User profile management
- Posting and editing ads
- Searching and filtering ads
- Responsive design using Bootstrap

## Technologies Used

- Django (Python web framework)
- Bootstrap (CSS framework)
- Easy Thumbnails (for image handling)
- SQLite (default database)

## Installation

1. **Clone the repository:**

    ```sh
    git clone https://github.com/yourusername/adboards.git
    cd adboards
    ```

2. **Create a virtual environment and activate it:**

    ```sh
    python -m venv venv
    venv\Scripts\activate  # On Windows
    # source venv/bin/activate  # On macOS/Linux
    ```

3. **Install the dependencies:**

    ```sh
    pip install -r requirements.txt
    ```

4. **Apply migrations:**

    ```sh
    python manage.py migrate
    ```

5. **Create a superuser:**

    ```sh
    python manage.py createsuperuser
    ```

6. **Run the development server:**

    ```sh
    python manage.py runserver
    ```

7. **Open your browser and go to:**

    ```
    http://127.0.0.1:8000/
    ```

## Usage

- **Home Page:** Browse the latest ads.
- **Profile:** Manage your profile and view your posted ads.
- **Post Ad:** Create a new ad.
- **Search:** Use the search bar to find ads.

## Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes.
4. Commit your changes (`git commit -m 'Add some feature'`).
5. Push to the branch (`git push origin feature-branch`).
6. Open a pull request.
