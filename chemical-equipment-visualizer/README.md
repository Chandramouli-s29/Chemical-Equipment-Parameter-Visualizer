# Chemical Equipment Parameter Visualizer

A hybrid Web + Desktop application for visualizing and analyzing chemical equipment parameters. Upload CSV files containing equipment data and get instant insights through interactive charts, summary statistics, and PDF reports.

## Quick Start

```bash
# 1. Start Backend (Terminal 1)
cd backend
pip install -r requirements.txt
python setup_and_run.py

# 2. Start Web Frontend (Terminal 2)
cd web-frontend
bash setup_and_run.sh

# 3. Login with: admin / admin
```

## Features

- **CSV Upload**: Upload equipment data via Web (React) or Desktop (PyQt5) interface
- **Data Visualization**: Interactive charts using Chart.js (Web) and Matplotlib (Desktop)
- **Summary Statistics**: Automatic calculation of averages, min/max values, and type distributions
- **History Management**: Store and manage last 5 uploaded datasets
- **PDF Reports**: Generate and download detailed PDF reports
- **Authentication**: Basic authentication for secure access
- **Responsive Design**: Modern UI with Tailwind CSS

## Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| Frontend (Web) | React.js + Chart.js | Web interface with interactive charts |
| Frontend (Desktop) | PyQt5 + Matplotlib | Desktop application with native charts |
| Backend | Django + Django REST Framework | REST API and data processing |
| Data Handling | Pandas | CSV parsing and analytics |
| Database | SQLite | Store last 5 uploaded datasets |
| PDF Generation | ReportLab | PDF report generation |

## Project Structure

```
chemical-equipment-visualizer/
├── backend/                    # Django REST API
│   ├── chemical_equipment_visualizer/  # Django project settings
│   ├── equipment/              # Equipment app (models, views, serializers)
│   ├── manage.py
│   └── requirements.txt
├── web-frontend/               # React web application
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── lib/                # API client and utilities
│   │   ├── App.tsx
│   │   └── ...
│   ├── package.json
│   └── ...
├── desktop-frontend/           # PyQt5 desktop application
│   ├── main.py
│   └── requirements.txt
└── sample_data/
    └── sample_equipment_data.csv  # Sample data for testing
```

## Prerequisites

- Python 3.8+
- Node.js 18+
- pip
- npm

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd chemical-equipment-visualizer
```

### 2. Backend Setup (Django)

**Quick Setup (Recommended):**
```bash
cd backend
pip install -r requirements.txt
python setup_and_run.py
```

**Manual Setup:**
```bash
# Navigate to backend directory
cd backend

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations (this will also create the default admin user: admin / admin)
python manage.py migrate

# Start Django development server
python manage.py runserver
```

The backend API will be available at `http://localhost:8000/api/`

### 3. Web Frontend Setup (React)

Open a new terminal window:

**Quick Setup:**
```bash
cd web-frontend
bash setup_and_run.sh
```

**Manual Setup:**
```bash
# Navigate to web-frontend directory
cd web-frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The web application will be available at `http://localhost:5173`

### 4. Desktop Frontend Setup (PyQt5)

Open a new terminal window:

```bash
# Navigate to desktop-frontend directory
cd desktop-frontend

# Install dependencies (use the backend virtual environment or create new)
pip install -r requirements.txt

# Run the desktop application
python main.py
```

## Usage

### Default Credentials

- **Username**: `admin`
- **Password**: `admin`

> **Note**: The admin user is automatically created when you run `python manage.py migrate`. If you need to recreate it, run `python manage.py createsuperuser`.

### Web Application

1. Open your browser and navigate to `http://localhost:5173`
2. Login with the default credentials
3. Upload a CSV file using the upload form
4. View data tables, charts, and summary statistics
5. Download PDF reports

### Desktop Application

1. Run `python main.py`
2. Login with the default credentials
3. Click on the upload area to select a CSV file
4. Enter a dataset name and click "Upload & Analyze"
5. Navigate between Charts and Data Table tabs
6. Download PDF reports

### CSV File Format

The CSV file should contain the following columns:

```csv
Equipment Name,Type,Flowrate,Pressure,Temperature
Pump-A101,Centrifugal Pump,125.5,4.2,65.3
Heat Exchanger-HX101,Shell and Tube,45.6,3.5,145.8
```

**Required Columns:**
- `Equipment Name` - Name of the equipment
- `Type` - Type/category of equipment

**Optional Columns:**
- `Flowrate` - Flow rate value
- `Pressure` - Pressure value
- `Temperature` - Temperature value

### Sample Data

A sample CSV file is provided at `sample_data/sample_equipment_data.csv` for testing.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/datasets/` | GET | List all datasets |
| `/api/datasets/` | POST | Create new dataset |
| `/api/datasets/{id}/` | GET | Retrieve dataset details |
| `/api/datasets/{id}/` | DELETE | Delete a dataset |
| `/api/datasets/upload_csv/` | POST | Upload CSV file |
| `/api/datasets/{id}/summary/` | GET | Get summary statistics |
| `/api/datasets/{id}/data/` | GET | Get all data items |
| `/api/datasets/{id}/chart_data/` | GET | Get chart data |
| `/api/datasets/{id}/generate_pdf/` | GET | Download PDF report |

## Screenshots

### Web Application
- Login page with modern design
- Dashboard with summary cards
- Interactive charts (Pie, Bar, Line)
- Data table with pagination
- History management

### Desktop Application
- Native PyQt5 interface
- Matplotlib charts
- Tabbed navigation
- File browser integration

## Development

### Backend Development

```bash
cd backend
python manage.py runserver
```

### Web Frontend Development

```bash
cd web-frontend
npm run dev
```

### Build for Production

**Web Frontend:**
```bash
cd web-frontend
npm run build
```

The built files will be in `web-frontend/dist/`.

## Troubleshooting

### Backend Issues

1. **Database errors**: Run `python manage.py migrate`
2. **Port already in use**: Change port with `python manage.py runserver 8080`
3. **CORS errors**: Ensure `CORS_ALLOW_ALL_ORIGINS = True` in settings.py

### Web Frontend Issues

1. **npm install fails**: Delete `node_modules` and try again
2. **API connection errors**: Ensure backend is running on port 8000
3. **Build errors**: Check Node.js version (18+ required)

### Desktop Frontend Issues

1. **PyQt5 install fails**: Install system dependencies first
   - Ubuntu/Debian: `sudo apt-get install python3-pyqt5`
   - macOS: `brew install pyqt5`
2. **Matplotlib backend errors**: Ensure `matplotlib.use('Qt5Agg')` is set

## License

This project is licensed under the MIT License.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Contact

For questions or support, please open an issue on GitHub.

## Recent Fixes Applied

During a debugging pass the following fixes were applied to improve CSV upload reliability and API responses:

- Frontend: ensured multipart `FormData` uploads are sent without forcing a `Content-Type` header so the browser/axios can set the multipart boundary correctly.
- Backend: converted pandas/numpy numeric types to native Python types before saving `summary_data` so JSON serialization no longer fails (fixes "int64 is not JSON serializable").
- Backend: added a conservative header-mapping fallback and delimiter autodetection so common CSV header variants (e.g. `name`, `equipment_name`) map to the required `Equipment Name` column when possible.
- API: clearer validation error responses include received columns to aid debugging.

If you encounter further CSV upload issues, please paste the request/response from your browser DevTools (Network → POST to `/api/datasets/upload_csv/`).

---

**Note**: This is a demo application. For production use, please:
- Use a production-grade database (PostgreSQL/MySQL)
- Enable proper authentication (JWT/OAuth)
- Set up HTTPS
- Configure proper CORS settings
- Use environment variables for sensitive settings
