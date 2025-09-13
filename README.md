# 🏏 Cricbuzz LiveStats: Real-Time Cricket Insights & SQL-Based Analytics

A comprehensive cricket analytics dashboard that integrates live data from the Cricbuzz API with advanced SQL database operations.

## 🚀 Quick Start

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application:**
   ```bash
   cd cricbuzz_livestats
   streamlit run app.py
   ```

3. **Open Browser:**
   Navigate to `http://localhost:8501`

## 🎯 Features

- **📺 Live Matches** - Real-time scores and commentary
- **📊 Player Statistics** - Comprehensive batting/bowling stats  
- **🔍 25+ SQL Queries** - Beginner to advanced analytics
- **🛠️ CRUD Operations** - Full database management
- **📱 Modern UI** - Responsive dark theme design

## 🏗️ Architecture

- **Frontend:** Streamlit with modern CSS styling
- **Backend:** SQLite database with pandas
- **API:** Cricbuzz RapidAPI integration
- **Analytics:** 25+ SQL queries from basic to advanced

## 📊 SQL Query Categories

### 🟢 Beginner (1-8)
- Basic SELECT, WHERE, GROUP BY operations
- Simple aggregations and filtering

### 🟡 Intermediate (9-16)  
- JOINs, subqueries, complex aggregations
- Multi-table analysis

### 🔴 Advanced (17-25)
- Window functions, CTEs, analytical functions
- Performance rankings and trend analysis

## 🛠️ Technical Stack

- **Python 3.9+**
- **Streamlit** - Web framework
- **SQLite** - Database
- **Pandas** - Data manipulation
- **Plotly** - Visualizations  
- **Requests** - API integration

## 📁 Project Structure

```
cricbuzz_livestats/
├── app.py                 # Main application
├── requirements.txt       # Dependencies
├── pages/                 # Streamlit pages
│   ├── home.py
│   ├── live_matches.py
│   ├── top_stats.py
│   ├── sql_queries.py
│   └── crud_operations.py
├── utils/                 # Utilities
│   ├── api_utils.py       # API management
│   └── db_connection.py   # Database operations
└── notebooks/             # Testing scripts
    └── data_fetching.py
```

## 🎓 Educational Value

Perfect for learning:
- **SQL** - 25 queries from basic to advanced
- **API Integration** - REST API consumption
- **Database Design** - Normalized cricket schema
- **Web Development** - Modern Streamlit applications
- **Data Analytics** - Sports statistics analysis

## 🏏 Business Applications

- **Sports Media** - Real-time commentary support
- **Fantasy Cricket** - Player analysis and selection
- **Cricket Analytics** - Advanced statistical modeling
- **Education** - SQL learning with real cricket data

## 🔑 API Configuration

Update the API key in `utils/api_utils.py`:
```python
self.headers = {
    "X-RapidAPI-Key": "YOUR_RAPIDAPI_KEY_HERE",
    "X-RapidAPI-Host": "cricbuzz-cricket.p.rapidapi.com"
}
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License.

## 👨‍💻 Author

Built with ❤️ for cricket analytics enthusiasts and data science learners.

---
**🏏 Cricbuzz LiveStats** - Where Cricket Meets Data Science!
