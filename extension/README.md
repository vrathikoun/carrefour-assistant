This folder contains the Carrefour Assistant browser extension. This extension is built using standard web technologies (HTML, CSS, JavaScript) and interacts with the backend services to provide users with product, recipe, and store information directly within their browser.

## Architecture

The extension is structured into several key components:

- **`manifest.json`**: This file provides important information about the extension, such as its name, version, permissions, and background scripts. It's the entry point for the browser to understand and load the extension.
- **`popup.html`**: This is the HTML file for the extension's popup window, which appears when the user clicks the extension icon in the browser toolbar. It defines the structure and content of the user interface.
- **`popup.js`**: This JavaScript file contains the logic for the `popup.html`. It handles user interactions within the popup, makes requests to the backend, and updates the UI with the retrieved data.
- **`popup.css`**: This CSS file styles the `popup.html`, ensuring a consistent and user-friendly appearance.
- **`background.js`**: This script runs in the background and handles events that are not directly tied to the popup UI, such as listening for browser events (e.g., tab updates, navigation) or making API calls that don't require immediate user interaction.
- **`content.js`**: This script is injected into web pages that the user visits. It can interact with the DOM of the visited page, extract information, or inject new UI elements. This is useful for providing context-aware assistance.
- **`icons/`**: This directory contains the various icon files used by the extension (e.g., for the browser toolbar, manifest).

## How to Develop and Test

1.  **Load the extension in your browser:**
    *   **Chrome:**
        1.  Open Chrome and navigate to `chrome://extensions`.
        2.  Enable "Developer mode" (usually a toggle in the top right).
        3.  Click "Load unpacked" and select this `extension/` folder.
    *   **Firefox:**
        1.  Open Firefox and navigate to `about:debugging#/runtime/this-firefox`.
        2.  Click "Load Temporary Add-on..." and select any file inside this `extension/` folder (e.g., `manifest.json`).

2.  **