# JobSpy Scraper API

This API is a robust backend service designed to perform large-scale, automated scraping of job postings from **LinkedIn** and **Indeed**. It stores the data efficiently in a database and provides a clean RESTful API to manage and retrieve the collected information.

The project is built with a modern Python stack, including FastAPI for the API, SQLAlchemy for database interaction, and Supabase for the PostgreSQL backend.

-----

## ✨ Key Features

  - **Automated Job Scraping:** Fetches job data from LinkedIn and Indeed based on a configurable list of keywords.
  - **Dynamic Keyword Management:** Easily manage which job titles and locations to scrape by editing the `keywords.json` file.
  - **Company & Title Blocking System:** A built-in API to block specific companies or job titles from appearing in the results, ensuring cleaner data.
  - **Smart Data Deduplication:** Automatically avoids saving duplicate job entries to maintain a clean database.
  - **Full CRUD API for Data Access:** Endpoints to search, retrieve with pagination, and delete jobs and blocked entities.
  - **Automated Scheduling:** Includes a script to run the scraping process automatically on a schedule (e.g., daily).
  - **Background Processing:** The scraping task runs in the background, allowing the API to remain responsive.

-----

## ⚙️ Setup and Installation

### 1\. Clone the Repository

```bash
git clone https://github.com/bintangampuh/jobspy.git
cd jobspy
```

### 2\. Create and Activate a Virtual Environment

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

```bash
pip install -r requirements.txt
```

### 4\. Configure Environment Variables

1.  Create a new file named `.env` in the project's root directory.

2.  Fill the `.env` file with your Supabase and ScraperAPI credentials. For best performance, use the **Transaction Pooler** connection details from your Supabase dashboard.

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

### 5\. Configure Keywords for Scraping

Open the `keywords.json` file and edit the lists to define which job titles and locations you want to scrape.

```json
{
  "job_titles": ["Software Engineer", "Data Analyst", "Product Manager"],
  "locations": ["Indonesia", "Singapore"]
}
```

### 6\. Prepare the Database

Run the following script **only once** to create the necessary tables (`scraped_jobs`, `job_matches`, and `blocked_entities`) in your Supabase database.

```bash
python create_tables.py
```

### 7\. Run the API Server

Use Uvicorn to start the FastAPI server. The `--reload` flag enables hot-reloading for development.

```bash
uvicorn main:app --reload
```

The server will be running on `http://127.0.0.1:8000`.

-----

## 🚀 API Usage and Endpoints

Use an API client like Postman or Insomnia to interact with the following endpoints.

### Job Data Structure

All endpoints that return job data will use the following JSON structure for each job object:

```json
{
  "id": 1,
  "title": "Senior Python Developer",
  "company_name": "Tech Solutions Inc.",
  "location": "Jakarta, Indonesia",
  "job_url": "https://www.linkedin.com/jobs/view/...",
  "date_scraped": "2025-09-10T12:00:00Z"
}
```

### Scraping

  - **`POST /scrape/start`**
      - **Description:** Triggers the background scraping task based on `keywords.json`.
      - **Response:** `{ "message": "Scraping process has been started..." }`

### Retrieving Jobs

  - **`GET /jobs/`**

      - **Description:** Fetches a paginated list of all scraped jobs.
      - **Query Parameters:**
          - `skip` (optional, integer, default: `0`): The number of records to skip.
          - `limit` (optional, integer, default: `10`): The maximum number of records to return.
      - **Example:** `http://127.0.0.1:8000/jobs/?skip=10&limit=20`

  - **`GET /jobs/search`**

      - **Description:** Performs a more specific job search based on multiple criteria.
      - **Query Parameters:**
          - `q` (optional, string): A keyword to search for in the **job title**.
          - `location` (optional, string): The name of the job **location**.
          - `page` (optional, integer, default: `1`): The page number for the search results.
          - `limit` (optional, integer, default: `10`): The number of results per page.
      - **Usage Examples:**
          - By keyword only: `http://127.0.0.1:8000/jobs/search?q=Controller`
          - By location only: `http://127.0.0.1:8000/jobs/search?location=Amsterdam`
          - Full combination: `http://127.0.0.1:8000/jobs/search?q=Accountant&location=Haarlem&page=1&limit=5`

  - **`DELETE /jobs/{job_id}`**

      - **Description:** Deletes a specific job from the database by its ID.
      - **Example:** `http://127.0.0.1:8000/jobs/1`

### Managing the Blocklist

  - **`POST /block/`**

      - **Description:** Adds a company or title to the blocklist.
      - **Request Body:** `{ "entity_type": "company", "entity_value": "Example Corp" }`

  - **`GET /block/`**

      - **Description:** Retrieves a list of all currently blocked companies and titles.

  - **`DELETE /block/{entity_id}`**

      - **Description:** Deletes a specific entity from the blocklist by its ID.
      - **Example:** `http://127.0.0.1:8000/block/1`

-----

## 🕒 Advanced Usage: Automated Scheduling

To run the scraping process automatically at a set interval (e.g., once a day), you can run the `scheduled_task.py` script. This script will run continuously in the background, triggering the scraping process once every 24 hours after its initial launch.

```bash
python scheduled_task.py
```
