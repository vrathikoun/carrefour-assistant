# Backend

This folder contains the backend services for the Carrefour Assistant application. It is built using Python and Flask, and interacts with various APIs to provide information about products, recipes, and store locations.

## Architecture

The backend is organized into several key components:

- **`app.py`**: This is the main entry point of the Flask application. It initializes the Flask app, registers blueprints, and sets up configurations.
- **`config.py`**: This file handles the configuration settings for the application, such as API keys, database connections, and other environment-specific variables.
- **`routes/`**: This directory contains the different API endpoints (routes) of the application, organized by functionality. Each file within this directory typically defines a blueprint and its associated routes.
    - **`product_routes.py`**: Handles requests related to product information, such as searching for products, retrieving product details, and potentially managing product data.
    - **`recipe_routes.py`**: Manages requests for recipe information, including searching for recipes, fetching recipe details, and potentially integrating with recipe APIs.
    - **`store_routes.py`**: Deals with requests related to Carrefour store locations, opening hours, and other store-specific information.
- **`services/`**: This directory contains the business logic and external API integrations. Each file here typically encapsulates the logic for interacting with a specific external service or performing a particular business operation.
    - **`product_service.py`**: Contains the logic for interacting with product-related APIs (e.g., Carrefour product API, Open Food Facts).
    - **`recipe_service.py`**: Implements the logic for fetching and processing recipe data from external recipe APIs.
    - **`store_service.py`**: Handles the communication with store location APIs or internal store data sources.
- **`utils/`**: This directory holds utility functions and helper classes that are used across different parts of the application.
    - **`api_clients.py`**: Contains classes or functions for making HTTP requests to external APIs, potentially handling authentication and error handling.
    - **`decorators.py`**: Provides custom decorators for common tasks like authentication, logging, or input validation.
    - **`helpers.py`**: A general-purpose file for various helper functions that don't fit into other specific categories.
- **`models/`**: (