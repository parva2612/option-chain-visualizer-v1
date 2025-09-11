# Option Chain Dashboard

This is a Dash application to visualize option chain data stored in Parquet files. It allows selecting expiry, datetime, and displays the corresponding option chain along with SPOT and ATM highlighting.

---

## How to Run

1. **Create a virtual environment** (optional but recommended):

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.\.venv\Scripts\activate  # Windows
```

2. **Install dependencies:**

```bash
pip install -r requirements.txt
```

3. **Prepare your data:**

   * Store your Parquet files in the `data/` folder.
   * Each file should be named as `<expiry>.parquet`, for example: `09SEP25.parquet`.

4. **Launch the app:**

```bash
python app.py
```

5. **Open in browser:**

   * Go to `http://127.0.0.1:8050/`.

---

## Data Format

Each Parquet file should contain:

* **Datetime column:**

  * Column name: `datetime`
  * Format: any parsable timestamp (`YYYY-MM-DD HH:MM:SS` recommended)

* **SPOT column:**

  * Column name: `SPOT`
  * Contains the underlying spot price for that datetime.

* **Option columns:**

  * Column names should follow the pattern: `<prefix><strike><CE/PE>`
  * Example: `NIFTY09SEP2523500CE`, `NIFTY09SEP2523500PE`
  * The strike is extracted from the digits in the column name, ignoring the last two digits of expiry if present.
  * Values can be:

    * Price only, or
    * OHLC as a dictionary (`{"open":..., "high":..., "low":..., "close":...}`) or a 4-item list/tuple.

---

## Workflow

1. **Load Data:**

   * The app reads all Parquet files in the `data/` folder.
   * Loaded data is cached in memory to improve performance.

2. **Expiry Selection:**

   * Dropdown populated with available expiry files.
   * Selecting an expiry loads its option chain.

3. **Datetime Selection:**

   * Enter a datetime to see the option chain at that timestamp.
   * If the exact datetime is not found, the nearest available datetime is used and suggested.

4. **Display:**

   * Option chain table shows CE, strike, and PE columns.
   * The current datetime being displayed is shown.
   * SPOT value and ATM strike (nearest 50 to SPOT) are displayed.
   * The ATM row is highlighted for easy reference.

5. **User Interaction:**

   * Changing expiry or datetime updates the table and info dynamically.
   * The table and highlights update automatically based on the data.

---

This structure ensures the app can handle multiple expiries, dynamic datetime selection, and provides a clear visualization of option chain data.
