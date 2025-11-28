# NPS Analysis Desktop App

A cross-platform desktop application for automated Net Promoter Score (NPS) analysis with advanced demographic weighting.

## Features

*   **Automated Analysis**: Upload your survey data and get instant NPS and Top Box scores.
*   **Advanced Weighting**: Uses **Iterative Proportional Fitting (Raking)** to balance your sample against population targets across multiple variables (Gender, Age, Region, etc.).
*   **Subset Weighting**: Automatically recalculates weights for specific subgroups when analyzing by segments (e.g., analyzing "Seoul" respondents separately).
*   **Visual Dashboard**: Interactive charts for NPS Breakdown, Score Distribution, and Comparative Analysis.
*   **Cross-Platform**: Runs on macOS (and Windows/Linux via Electron).

## Installation

### macOS
1.  Download the `.dmg` file from the [Releases](https://github.com/dataofmen/nps-analysis-desktop/releases) page.
2.  Open the `.dmg` and drag **NPS Analysis.app** to your **Applications** folder.
3.  **Important**: If you see a "damaged" error, please read the [Installation Guide](INSTALL_GUIDE.md) for the fix.

## Documentation

*   **[Installation Guide](INSTALL_GUIDE.md)**: Troubleshooting installation issues.
*   **[Weighting Methodology](WEIGHTING_METHODOLOGY.md)**: Learn how the Raking algorithm works.
*   **[Verification Guide](VERIFICATION_GUIDE.md)**: How to manually verify the analysis results.

## Development

### Prerequisites
*   Node.js (v18+)
*   Python (v3.10+)
*   `pip` and `npm`

### Setup
1.  Clone the repository.
2.  Install Backend dependencies:
    ```bash
    cd backend
    pip install -r requirements.txt
    ```
3.  Install Frontend dependencies:
    ```bash
    cd frontend
    npm install
    ```

### Running Locally
1.  Start the Backend:
    ```bash
    cd backend
    uvicorn main:app --reload --port 8000
    ```
2.  Start the Frontend (Electron Dev Mode):
    ```bash
    cd frontend
    npm run electron:dev
    ```

### Building for Production
1.  Build the Backend executable:
    ```bash
    ./backend/build_backend.sh
    ```
2.  Build the Electron App:
    ```bash
    cd frontend
    npm run electron:build
    ```
