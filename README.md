# Recipe API

This project is a Recipe API created as an assessment test for an internship. The API allows users to manage recipes, rate them, and comment on them. It also includes user authentication and authorization.

## Features

- Add, update, delete, and retrieve recipes
- Rate and comment on recipes
- Search for recipes by name or ingredients
- Suggest recipes based on provided ingredients
- User authentication and authorization

## Prerequisites

- Docker and Docker Compose
- Python 3.8 or later

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/AxcelT/RecipeAPI.git
    cd recipe-api
    ```

2. Set up a virtual environment and install dependencies:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    pip install -r requirements.txt
    ```

## Usage

1. Run the application using Docker:
    ```sh
    docker-compose up --build
    ```

2. The API will be available at `http://localhost:8000`.

## API Endpoints

### Recipe Management

- **POST /recipes/**: Add a new recipe.
- **GET /recipes/**: Retrieve a list of all recipes, sorted by most recent.
- **GET /recipes/{recipe_id}/**: Retrieve details of a specific recipe by its ID.
- **PUT /recipes/{recipe_id}/**: Update a specific recipe by its ID.
- **DELETE /recipes/{recipe_id}/**: Delete a specific recipe by its ID.

### Rating and Commenting

- **POST /recipes/{recipe_id}/ratings/**: Rate a specific recipe. Accepts a rating (1-5).
- **POST /recipes/{recipe_id}/comments/**: Comment on a specific recipe. Accepts a comment text.
- **GET /recipes/{recipe_id}/comments/**: Retrieve all comments for a specific recipe.

### User Management

- **POST /users/**: Create a new user. Accepts a username, email, and password.
- **POST /token**: Obtain a JWT token for authentication. Accepts a username and password.

### Search and Suggest

- **GET /recipes/search/**: Search recipes by name or ingredients. Accepts a query parameter.
- **GET /recipes/suggestions/**: Suggest recipes based on provided ingredients. Accepts a list of ingredients.

## Running Tests

1. Run the tests:
    ```sh
    pytest tests
    ```

## Docker Instructions

1. Build and run the containers:
    ```sh
    docker-compose up --build
    ```

## Contributors

- Axcel Justin D. Tidalgo (axcel_tidalgo@dlsu.edu.ph)
