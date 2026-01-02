# 💰 AI Expense Tracker

A modern, AI-powered expense tracking application built with Streamlit that helps you manage your personal finances using Google Sheets for storage and interactive analytics.

---

## ✨ Features

### **Home.py – Transaction Management**

- 📋 View existing transactions from Google Sheets
- ➕ Add new transactions via a user-friendly form:
  - Date, Amount, Type (Income/Expense)
  - Category, Subcategory, Description
  - Due Date and Status (PENDING/COMPLETED)
- 🗂️ Data appended directly to Google Sheets
- 🎨 Responsive UI with custom cards
- 🌙 Dark mode toggle for better viewing experience
- 🔗 Quick access link to Google Sheet from sidebar

### **Analytics.py – Financial Insights**

- 📈 Overview Tab
  - Total Income, Total Expense, Net Savings, Saving Rate
  - Dynamic metric boxes with dark/light mode styling
  - Monthly Income vs Expense bar chart
- 💰 Income Tab
  - Monthly income trend visualization
- 💸 Expense Tab
  - Monthly expense trend visualization
  - Category-wise expense breakdown (pie chart)
- 📋 Pending Tab
  - View all pending transactions
- 🗓️ Sidebar Filters
  - All Time, Year, Month, Custom Range
- ⚡ Google Sheets Integration
  - Columns handled: Date, Amount, Type, Category, Subcategory, Description, Due Date, Status
  - Automatic conversion of numeric and date fields
  - Invalid rows automatically dropped
- 🎨 Dark mode compatible charts and UI
- 🕒 Cached data for improved performance

---

## 🚀 Getting Started

### Prerequisites

1. **Python Environment**
   - Python 3.8 or higher
   - pip
2. **Google Cloud Setup**
   - Google Sheets API enabled
   - Service account with credentials JSON
3. **.env file**
   ```env
   GOOGLE_SHEETS_CREDENTIALS=path/to/your/credentials.json
   SPREADSHEET_ID=your_google_sheet_id
   GEMINI_API_KEY=your_gemini_api_key
   ```

---

## 🚀 Installation & Running

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configuration

### Transaction Categories

**Income Categories:**

- Salary
- Investments
- Business
- Other Income

**Expense Categories:**

- Food & Dining
- Shopping
- Transportation
- Bills & Utilities
- Entertainment
- Health & Wellness
- Other Expenses

### Pending Transaction Types

- To Pay (for upcoming payments)
- To Receive (for expected income)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Uses Google Sheets API for data storage
- Visualizations powered by Plotly
- Inspired by [Spritan/expense_tracker](https://github.com/Spritan/expense_tracker)

## 💡 Support

For support:

1. Check the documentation above
2. Open an issue in the GitHub repository
3. Contact the maintainers

## 🔒 Security Note

- Never commit your `.env` file or credentials to version control
- Keep your API keys and credentials secure
- Regularly rotate your service account keys
- Follow the principle of least privilege when setting up service accounts
