<div align="center">
  <h1>🔴 Pokémon Data Pipeline</h1>
  <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/25.png" width="200" alt="Pikachu">
  <p><i>A comprehensive ETL pipeline for fetching, transforming, and storing Pokémon data from PokeAPI</i></p>
</div>

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [Quick Start with Docker](#quick-start-with-docker)
3. [Manual Setup](#manual-setup)
4. [Running Tests](#running-tests)
5. [Project Structure](#project-structure)
6. [Design Choices](#design-choices)
7. [Features](#features)
8. [Future Improvements](#future-improvements)

## 🎯 Project Overview

This project implements a data pipeline that extracts Pokémon data from the public PokeAPI, transforms it into a structured relational format, and stores it in a SQL database. The solution includes a FastAPI backend for data processing and a React-based frontend for visualization and interaction with the Pokémon data.

## 🚀 Quick Start with Docker

The easiest way to run the entire application is using Docker Compose:

```bash
docker-compose up --build
```

This single command will:
- Build and start the SQLite database
- Launch the FastAPI backend server (http://localhost:8000)
- Start the React frontend application (http://localhost:3000)
- And on the click of a button run the data pipeline to fetch and store Pokémon data

**Access the application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## 🛠️ Manual Setup

If you prefer to run the services individually without Docker:

### Backend Setup

**Windows:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

**Linux/macOS:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

The backend will be available at http://localhost:8000

### Frontend Setup

```bash
cd frontend
npm install
npm start
```

The frontend will be available at http://localhost:3000

## 🧪 Running Tests

To run the test suite:

**Windows:**
```bash
cd backend
venv\Scripts\activate
pip install -r requirements_test.txt
pytest
```

**Linux/macOS:**
```bash
cd backend
source venv/bin/activate
pip install -r requirements_test.txt
pytest
```

**Run tests with coverage:**
```bash
pytest --cov=. --cov-report=html
```

## 📁 Project Structure

```
pokemon-data-pipeline/
├── backend/
│   ├── main.py                 # FastAPI application entry point
│   ├── pipeline/
│   │   ├── extract.py         # Data extraction from PokeAPI
│   │   ├── transform.py       # Data transformation logic
│   │   └── load.py            # Database loading operations
│   ├── models/
│   │   └── database.py        # SQLAlchemy models and schema
│   ├── tests/
│   │   ├── test_extract.py
│   │   ├── test_transform.py
│   │   └── ......
│   ├── requirements.txt
│   └── requirements_test.txt
├── frontend/
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── App.js
│   │   └── index.js
│   ├── package.json
│   └── public/
├── docker-compose.yml
└── README.md
```

## 🎨 Design Choices

### Data Transformation & Mapping

The pipeline transforms nested JSON data from PokeAPI into a normalized relational structure:

**Database Schema:**
- **pokemon** table: Stores core Pokémon information (id, name, height, weight, base_experience)
- **pokemon_types** table: Many-to-many relationship for Pokémon types
- **pokemon_abilities** table: Many-to-many relationship for abilities
- **pokemon_stats** table: One-to-many relationship for base stats (HP, Attack, Defense, etc.)

**Mapping Decisions:**
1. **Normalization**: Separated types, abilities, and stats into distinct tables to avoid data redundancy
2. **Type Safety**: Used appropriate SQL data types (INTEGER for stats, VARCHAR for names)
3. **Relationships**: Implemented foreign key constraints to maintain referential integrity
4. **Indexing**: Added indexes on frequently queried fields (name, type) for performance

### Technology Choices

- **FastAPI**: Chosen for its async capabilities, automatic API documentation, and type validation
- **SQLAlchemy**: Provides ORM capabilities with support for multiple database backends
- **PostgreSQL**: Robust relational database with excellent JSON support for future enhancements
- **React**: Modern, component-based frontend framework for building interactive UIs
- **Docker**: Ensures consistent environment across development and deployment

## ✨ Features

### Core Features
- ✅ Extracts data for 20+ Pokémon from PokeAPI
- ✅ Transforms nested JSON into normalized relational structure
- ✅ Stores data in PostgreSQL database
- ✅ Comprehensive documentation

### Optional Features Implemented
- ✅ **Clean, Pythonic Code**: Type hints, docstrings, and proper error handling
- ✅ **Containerization**: Full Docker and Docker Compose setup
- ✅ **Interactive Frontend**: React-based UI for viewing and filtering Pokémon
- ✅ **Testing**: Comprehensive test suite with pytest
- ✅ **API Endpoints**: RESTful API for accessing Pokémon data
- ✅ **Logging**: Structured logging for pipeline operations

## 🔮 Future Improvements

Given more time, the following enhancements would be valuable:

1. **GraphQL API**: Implement a GraphQL endpoint for more flexible data querying
2. **Advanced Relationships**: Add evolution chains and Pokémon form variations
3. **Caching Layer**: Implement Redis caching for frequently accessed data
4. **Incremental Updates**: Add functionality to update only changed Pokémon data
5. **Background Jobs**: Use Celery for asynchronous pipeline execution
6. **Authentication**: Add user authentication for personalized Pokémon collections
7. **Advanced Filtering**: Enhanced search with filters for multiple types, stat ranges, etc.
8. **Data Visualization**: Add charts and graphs for stat comparisons
9. **CI/CD Pipeline**: Automated testing and deployment workflows
10. **Monitoring**: Integrate application performance monitoring (e.g., Prometheus, Grafana)

## 🤝 Assumptions

- The PokeAPI structure remains consistent (as per v2 specification)
- Pokémon IDs 1-20 are fetched by default (configurable)
- Database credentials are managed via environment variables
- The application runs in a development environment (production deployment would require additional security measures)

## 📝 License

This project is open-source.

## 🙏 Acknowledgments

- Data provided by [PokeAPI](https://pokeapi.co/)
- Pokémon and Pokémon character names are trademarks of Nintendo

---

<div align="center">
  Made with ❤️ for the coding challenge
</div>
