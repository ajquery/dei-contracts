# Federal DEI Contracts Dashboard

An interactive dashboard for visualizing and analyzing federal DEI (Diversity, Equity, and Inclusion) contract data.

## Features

- Interactive filtering by date, agency, award size, and DEI themes
- Dynamic visualizations of contract data
- Summary statistics and key metrics
- Detailed contract information table
- Responsive design for both desktop and mobile

## Requirements

- Python 3.8+
- Required packages listed in `requirements.txt`

## Installation

1. Clone this repository or download the source code.

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Ensure your data file is located at:
   ```
   dei_contracts_master.csv
   ```

2. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```

3. Open your web browser and navigate to:
   ```
   http://localhost:8501
   ```

## Dashboard Components

### Filters (Sidebar)
- Date Range Selection
- Agency Filter
- Award Size Filter
- DEI Theme Selection

### Visualizations
1. Key Metrics
   - Total Contracts
   - Total Award Amount
   - Unique Recipients

2. Charts
   - DEI Themes Distribution
   - Award Amount Distribution by Top 10 Agencies
   - Timeline of Monthly Awards

3. Data Table
   - Detailed Contract Information
   - Sortable Columns

## File Structure

```
├── app.py              # Main Streamlit application
├── requirements.txt    # Python package requirements
├── dei_contracts_master.csv  # Data file
└── README.md          # This file
```

## Data Source

The dashboard uses a CSV file containing federal DEI contract data with the following key columns:
- Award ID
- Recipient Name
- Awarding Agency Name
- Award Amount
- Action Date
- Award Description
- DEI Themes

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 