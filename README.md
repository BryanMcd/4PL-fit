# 4PL-Fit

**4PL-Fit** is a tool designed for performing **4-Parameter Logistic (4PL) regression**, commonly used in bioassays like **ELISA** (Enzyme-Linked Immunosorbent Assay) to calculate sample concentrations from optical density (OD) readings.

The project offers two ways to use the tool:
1.  **Streamlit App**: A full-featured Python web application with interactive plotting and data editing.
2.  **Standalone HTML**: A single-file, client-side tool that runs directly in your browser without installation.

## Features

-   **Automatic Curve Fitting**: Fits a 4-parameter logistic model to your standard curve points.
    -   Equation: $y = D + \frac{A - D}{1 + (\frac{x}{C})^B}$
-   **Concentration Calculation**: Interpolates unknown sample concentrations based on the fitted curve.
-   **Interactive Graphs**: Visualizes the standard curve and sample points (using Plotly in Python, Chart.js in HTML).
-   **Data Management**: Supports CSV upload and manual data entry (copy-paste from Excel).
-   **Export**: Copy results table directly to your clipboard for easy transfer to Excel/Papers.

## Usage

### Option 1: Python Streamlit App

Recommended for robust analysis and if you are comfortable with Python.

#### Installation

1.  Clone this repository or download the files.
2.  Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

#### Running the App

Run the application using Streamlit:
```bash
streamlit run 4pl.py
```
This will automatically open the app in your default web browser (usually at `http://localhost:8501`).

### Option 2: Standalone HTML

Recommended for quick use without installing Python.

1.  Locate the file `4pl.html` in the project directory.
2.  Open it with any modern web browser (Chrome, Firefox, Safari, Edge).
3.  Drag and drop your CSV file or toggle to "Manual Spreadsheet" mode to paste data.

## Input Data Format (CSV)

Whether uploading a CSV or pasting data, the tool expects the following columns. The order does not strictly matter, but headers should match (case-insensitive key search is used).

| Type | Sample Name | Conc | OD_Rep1 | OD_Rep2 |
| :--- | :--- | :--- | :--- | :--- |
| Standard | | 5000 | 2.368 | 2.344 |
| Standard | | 2500 | 1.475 | 1.462 |
| ... | ... | ... | ... | ... |
| Sample | Control | | 0.52 | 0.507 |
| Sample | A1 | | 3.59 | 3.617 |

*   **Type**: Must contain "Standard" for calibration points or "Sample"/"Unknown" for test samples.
*   **Sample Name**: Identifier for your samples (optional for Standards).
*   **Conc**: Concentration value (Required for Standards, empty for Samples).
*   **OD_Rep1**, **OD_Rep2**: Optical Density values. You can have more replicate columns if needed.

## Quick maths

The curve is fitted using the standard 4PL equation:

$$
y = D + \frac{A - D}{1 + \left(\frac{x}{C}\right)^B}
$$

Where:
*   **x**: Concentration
*   **y**: Response (Optical Density)
*   **A**: Bottom asymptote (Background signal)
*   **D**: Top asymptote (Maximum signal)
*   **C**: $EC_{50}$ (Concentration at half-maximal response)
*   **B**: Hill slope (Steepness of the curve)