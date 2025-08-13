# SCRCPY Manager API

## Overview

SCRCPY Manager API is a modular API designed to manage and interact with Android and iOS devices using the SCRCPY tool. The API is structured to ensure that modifications in one platform do not affect the other, promoting maintainability and scalability.

## Features

- Modular architecture for Android and iOS.
- Health check endpoint to verify API status.
- Separate routers for device management, screenshots, and actions for both platforms.
- Configurable logging and middleware for error handling and request logging.

## Project Structure

```
device_manager_api
├── api
│   ├── main.py                # Entry point of the application
│   ├── config
│   │   └── settings.py        # Configuration settings
│   ├── middleware
│   │   ├── __init__.py        # Middleware initialization
│   │   └── logging.py         # Logging setup
│   ├── routers
│   │   ├── __init__.py        # Routers initialization
│   │   ├── common
│   │   │   └── __init__.py    # Common routers
│   │   ├── android
│   │   │   ├── device_router.py  # Android device routes
│   │   │   ├── screenshot_router.py  # Android screenshot routes
│   │   │   └── action_router.py  # Android action routes
│   │   └── ios
│   │       ├── device_router.py  # iOS device routes
│   │       ├── screenshot_router.py  # iOS screenshot routes
│   │       └── action_router.py  # iOS action routes
│   ├── utils
│   │   └── ensure_directory_exists.py  # Utility functions
│   └── models
│       ├── __init__.py        # Models initialization
│       ├── android.py         # Android data models
│       └── ios.py             # iOS data models
├── requirements.txt            # Project dependencies
└── README.md                   # Project documentation
```

## Installation

1. Clone the repository:

   ```
   git clone <repository-url>
   cd device_manager_api
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

To run the API, execute the following command:

```
python -m api.main
```

The API will start on the configured host and port. You can access the health check endpoint at:

```
http://<host>:<port>/api/health
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
