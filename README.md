# Web Scraper Backend

A full-stack web scraping solution using Python, FastAPI, Beautiful Soup, Selenium, and SQLite.

## 🍎 Quick Start for M1 Mac Users

If you have a Mac with Apple M1 chip, follow these optimized steps:

### Step 1: Install Homebrew (if not already installed)

Open Terminal (Cmd+Space, type "Terminal") and run:

\`\`\`bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
\`\`\`

After installation, follow the instructions to add Homebrew to your PATH.

### Step 2: Install Python

\`\`\`bash
brew install python@3.11
\`\`\`

Verify installation:
\`\`\`bash
python3 --version
\`\`\`

### Step 3: Install Google Chrome

Download and install from [google.com/chrome](https://www.google.com/chrome/)

### Step 4: Set Up the Project

Navigate to your project's backend folder:
\`\`\`bash
cd /Users/josmarybermudez/Desktop/final-project/backend
\`\`\`

Create and activate a virtual environment:
\`\`\`bash
python3 -m venv venv
source venv/bin/activate
\`\`\`

You should see `(venv)` at the start of your terminal prompt.

Install all dependencies:
\`\`\`bash
pip install -r requirements.txt
\`\`\`

This will take a few minutes. It's downloading all the necessary tools.

### Step 5: Run the Scraper

\`\`\`bash
python scraper.py
\`\`\`

You should see:
\`\`\`
🔍 Scraping products from: https://www.disco.com.ar/bebidas
⏳ Waiting for products to load...
✓ Successfully scraped 20 products
✓ Cleared products from database
✓ Inserted 20 products
✓ Scraping completed successfully!
\`\`\`

The scraper will create a `scraper.db` file in the backend folder automatically.

### Step 6: Start the API Server

\`\`\`bash
python main.py
\`\`\`

You should see:
\`\`\`
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
\`\`\`

### Step 7: Test It!

Open your browser and visit:
- API Documentation: http://localhost:8000/docs
- Get Products: http://localhost:8000/api/v1/products

### M1-Specific Troubleshooting

**If you get "architecture" errors:**
Some Python packages need to be compiled for ARM. If you see errors during `pip install`, try:
\`\`\`bash
# Install Rosetta 2 (allows running x86 apps)
softwareupdate --install-rosetta

# Then retry installation
pip install -r requirements.txt
\`\`\`

**If ChromeDriver fails:**
\`\`\`bash
# Install Chrome for Testing (ARM-native)
brew install --cask google-chrome
\`\`\`

**"Permission denied" when running scripts:**
\`\`\`bash
# Make sure you're using python3, not python
python3 scraper.py
python3 main.py
\`\`\`

### Quick Commands Reference

\`\`\`bash
# Activate virtual environment
source venv/bin/activate

# Run scraper
python scraper.py

# Start API server
python main.py

# Deactivate virtual environment when done
deactivate
\`\`\`

## 🚀 Complete Beginner's Guide (No Python Experience Required)

If you're new to Python, follow these steps carefully:

### Step 1: Install Python

**Windows:**
1. Go to [python.org/downloads](https://www.python.org/downloads/)
2. Download Python 3.11 or higher (click the big yellow button)
3. **IMPORTANT:** During installation, check the box "Add Python to PATH"
4. Click "Install Now"
5. Verify installation by opening Command Prompt and typing:
   \`\`\`bash
   python --version
   \`\`\`
   You should see something like `Python 3.11.x`

**macOS:**
1. Open Terminal (press Cmd+Space, type "Terminal")
2. Install Homebrew (if not installed):
   \`\`\`bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   \`\`\`
3. Install Python:
   \`\`\`bash
   brew install python@3.11
   \`\`\`
4. Verify:
   \`\`\`bash
   python3 --version
   \`\`\`

**Linux (Ubuntu/Debian):**
\`\`\`bash
sudo apt update
sudo apt install python3.11 python3-pip python3-venv
python3 --version
\`\`\`

### Step 2: Install Google Chrome

If you don't have Chrome installed:
1. Go to [google.com/chrome](https://www.google.com/chrome/)
2. Download and install Chrome browser
3. The scraper needs Chrome to load JavaScript on websites

### Step 3: Set Up the Project

1. **Open Terminal/Command Prompt**
   - Windows: Press Win+R, type `cmd`, press Enter
   - macOS: Press Cmd+Space, type "Terminal", press Enter
   - Linux: Press Ctrl+Alt+T

2. **Navigate to your project folder:**
   \`\`\`bash
   cd path/to/your/project/backend
   \`\`\`
   Replace `path/to/your/project` with the actual path where you downloaded the code.

3. **Create a virtual environment:**
   
   Windows:
   \`\`\`bash
   python -m venv venv
   \`\`\`
   
   macOS/Linux:
   \`\`\`bash
   python3 -m venv venv
   \`\`\`

4. **Activate the virtual environment:**
   
   Windows:
   \`\`\`bash
   venv\Scripts\activate
   \`\`\`
   
   macOS/Linux:
   \`\`\`bash
   source venv/bin/activate
   \`\`\`
   
   You should see `(venv)` appear at the start of your command line.

5. **Install all required packages:**
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`
   This will take a few minutes. It's downloading all the tools needed.

6. **Create environment file:**
   
   Windows:
   \`\`\`bash
   copy .env.example .env
   \`\`\`
   
   macOS/Linux:
   \`\`\`bash
   cp .env.example .env
   \`\`\`

### Step 4: Run the Scraper

Now you're ready to scrape products from Disco.com.ar!

\`\`\`bash
python scraper.py
\`\`\`

You should see output like:
\`\`\`
🔍 Scraping products from: https://www.disco.com.ar/bebidas
⏳ Waiting for products to load...
✓ Successfully scraped 20 products
✓ Cleared products from database
✓ Inserted 20 products
✓ Scraping completed successfully!
\`\`\`

The scraper will create a `scraper.db` file in the backend folder automatically.

### Step 5: Start the API Server

In the same terminal (with venv activated):

\`\`\`bash
python main.py
\`\`\`

You should see:
\`\`\`
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
\`\`\`

### Step 6: Test the API

Open your web browser and go to:
- **API Documentation:** http://localhost:8000/docs
- **Get Products:** http://localhost:8000/api/v1/products

You should see the 20 products scraped from Disco.com.ar!

### Common Issues for Beginners

**"python is not recognized" (Windows)**
- You forgot to check "Add Python to PATH" during installation
- Reinstall Python and make sure to check that box

**"Permission denied" errors**
- On macOS/Linux, try using `python3` instead of `python`
- On Linux, you might need `sudo` for some commands

**"Chrome not found"**
- Install Google Chrome browser (see Step 3)

**Virtual environment not activating**
- Make sure you're in the `backend` folder
- Try closing and reopening your terminal

### Need Help?

If you get stuck:
1. Read the error message carefully
2. Copy the error and search for it online
3. Make sure all steps above were completed
4. Check that Chrome is installed

## Features

- 🕷️ Web scraping with Beautiful Soup and Selenium (JavaScript support)
- 🚀 FastAPI REST API
- 🗄️ SQLite data persistence (no database server needed!)
- ✅ Pydantic data validation
- 🔄 Automatic data refresh (clears old data before inserting new)
- 🛡️ Error handling for network failures and page structure changes
- 🌐 Configured for Disco.com.ar (Argentine e-commerce site)

## Prerequisites

- Python 3.9 or higher
- Google Chrome browser (for Selenium)
- pip (Python package manager)

**That's it!** No database server installation needed - SQLite is built into Python.

## MongoDB Setup

**Note:** This project now uses SQLite instead of MongoDB. No database installation required!

SQLite creates a simple `scraper.db` file in your backend folder that stores all the data. It's perfect for local development and small to medium projects.

## Usage

### 1. Run the Scraper (Standalone)

To scrape products from Disco.com.ar and store them in SQLite:

\`\`\`bash
python scraper.py
\`\`\`

This will:
- Launch a headless Chrome browser
- Navigate to https://www.disco.com.ar/bebidas
- Wait for JavaScript to load products
- Scrape 20 products from the page
- Create `scraper.db` if it doesn't exist
- Clear existing products in the database
- Insert the newly scraped products

**Note:** First run may take longer as it downloads ChromeDriver.

### 2. Start the FastAPI Server

\`\`\`bash
python main.py
\`\`\`

Or using uvicorn directly:

\`\`\`bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
\`\`\`

The API will be available at: `http://localhost:8000`

### 3. API Endpoints

#### Get All Products
\`\`\`bash
GET http://localhost:8000/api/v1/products
\`\`\`

Response:
\`\`\`json
{
  "products": [
    {
      "product_name": "Sample Product",
      "price": 29.99,
      "image_url": "https://example.com/image.jpg"
    }
  ],
  "count": 20
}
\`\`\`

#### Trigger Manual Scrape
\`\`\`bash
POST http://localhost:8000/api/v1/scrape
\`\`\`

Response:
\`\`\`json
{
  "message": "Scraping completed successfully",
  "products_scraped": 20
}
\`\`\`

#### Health Check
\`\`\`bash
GET http://localhost:8000/
\`\`\`

### 4. API Documentation

FastAPI provides automatic interactive API documentation:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Project Structure

\`\`\`
backend/
├── main.py              # FastAPI application
├── scraper.py           # Web scraping logic
├── database.py          # SQLite connection and operations
├── models.py            # Pydantic models for validation
├── requirements.txt     # Python dependencies
├── scraper.db          # SQLite database (created automatically)
└── README.md           # This file
\`\`\`

## Configuration

### Environment Variables

- `SCRAPE_URL`: Target URL for scraping (default: `https://www.disco.com.ar/bebidas`)
- `API_HOST`: API server host (default: `0.0.0.0`)
- `API_PORT`: API server port (default: `8000`)

**Note:** No MongoDB connection string needed - SQLite uses a local file!

## Troubleshooting

### Database Issues
- **Database locked:** Make sure only one instance of the scraper or API is running
- **Permission errors:** Ensure you have write permissions in the backend folder
- The `scraper.db` file is created automatically - no setup needed!

### Scraping Issues
- **ChromeDriver errors:** The driver downloads automatically, but ensure Chrome browser is installed
- **No products found:** The site structure may have changed, or JavaScript didn't load in time
- **Timeout errors:** Increase the `time.sleep()` duration in `scraper.py`
- Check if the target URL is accessible
- Verify the HTML structure matches the selectors
- Check console output for specific error messages

## Production Deployment

For production deployment:

1. **For larger scale:** Consider migrating to PostgreSQL or MongoDB
2. Set up proper CORS origins
3. Use environment variables for sensitive data
4. Consider using a process manager (PM2, systemd)
5. Set up a reverse proxy (nginx)
6. Enable HTTPS
7. Implement rate limiting and authentication
8. **For Selenium in production:**
   - Use a headless browser service (e.g., Browserless, ScrapingBee)
   - Or deploy with Docker and include Chrome in the container
   - Consider using a scraping proxy to avoid IP blocks

## Why SQLite?

SQLite is perfect for this project because:
- ✅ No server installation or configuration needed
- ✅ Single file database - easy to backup and move
- ✅ Built into Python - zero setup
- ✅ Fast for small to medium datasets
- ✅ Perfect for local development and testing

For production with high traffic, consider PostgreSQL or MongoDB.

## License

MIT
