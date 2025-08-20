Of course. Here is the complete workflow for your project, from initial setup to running the scraper, written in English.

-----

# JobSpy Scraper API

This API serves as a backend service to perform large-scale scraping of job postings from LinkedIn and Indeed, store them in a database, and provide endpoints to manage the collected data. This project is built using FastAPI and SQLAlchemy, with Supabase as the PostgreSQL database.

## Key Features

  - **Hybrid Scraping:** Scrapes without a proxy for more lenient sites (Indeed) and with a proxy (ScraperAPI) for stricter sites (LinkedIn).
  - **Data Management:** Saves scraped results to a database, handles data deduplication, and provides endpoints for blocking companies.
  - **Background Processing:** The long-running scraping process is executed as a background task to avoid blocking the server.

-----

## ⚙️ Project Execution Steps

### 1\. Clone the Repository

```bash
git clone https://github.com/bintangampuh/jobspy.git
cd jobspy
```

### 2\. Create and Activate the Virtual Environment

  - **Windows:**
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```
  - **macOS/Linux:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

### 3\. Install Dependencies

All required libraries are listed in `requirements.txt`.

```bash
pip install -r requirements.txt
```

### 4\. Configure Environment Variables

1.  Copy the `.env.example` file (if it exists) or create a new file named `.env`.

2.  Fill the `.env` file with your credentials. Use the details from the **Transaction Pooler** in your Supabase dashboard for a more reliable connection.

    ```.env
    # Credentials from Supabase Dashboard (Use Transaction Pooler)
    DB_USER="postgres.xxxxxxxx"
    DB_PASSWORD="your-password"
    DB_HOST="aws-0-xx-xx-1.pooler.supabase.com"
    DB_PORT="6543"
    DB_NAME="postgres"

    # API Key from ScraperAPI
    SCRAPERAPI_API_KEY="your-apikey"
    ```

### 5\. Prepare the Database

Run the following script **only once** to create all the necessary tables in your Supabase database.

```bash
python create_tables.py
```

Verify in your Supabase dashboard under the "Table Editor" section to ensure that the `scraped_jobs`, `job_matches`, and `blocked_entities` tables have been created.

### 6\. Run the API Server

Use Uvicorn to run the FastAPI server. The `--reload` option will automatically restart the server whenever you save changes to your code.

```bash
uvicorn main:app --reload
```

If successful, you will see the message `Uvicorn running on http://127.0.0.1:8000`.

-----

## 🚀 Starting the Scraping Process

The scraping process does not start automatically. You must trigger it via an API endpoint.

1.  Open Postman or another API Client.
2.  Create a new request with the following details:
      - **Method:** `POST`
      - **URL:** `http://127.0.0.1:8000/scrape/start`
3.  Click **Send**.
4.  You will receive a response like `{ "message": "Proses scraping telah dimulai..." }`.
5.  **Monitor your VS Code terminal window** to see the logs and the progress of the scraping process in real-time.
