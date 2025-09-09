# 🔮 Crypto Price Prediction App

This project is a cryptocurrency price prediction tool that leverages **Deep Learning (LSTM, BiLSTM)** models to forecast future price movements based on historical market data.  
The results are automatically saved into a CSV file and can also be synced to a GitHub repository.

---

## 📑 Table of Contents
- [Features](#Features)
- [Requirements](#Requirements)
- [Installation](#Installation)
- [Usage](#Usage)
- [Project Structure](#Project-structure)
- [How It Works](#How-it-works)
- [Contributing](#Contributing)
- [License](#License)

---

## ✨ Features
- Automated cryptocurrency price forecasting using **Deep Learning** (LSTM + BiLSTM).
- Supports multiple time intervals:
  - Daily (`d`)
  - Weekly (`w`)
  - Monthly (`m`)
  - Yearly (`y`)
- **Automatic data fetching** – each token’s historical price data is downloaded on its scheduled day and stored in the `token-history` folder.
- Cleans noisy data with **Isolation Forest** before training.
- Flexible AI configurations depending on the prediction interval.
- Saves results in `result.csv` for easy tracking.
- Automatically updates predictions to a connected **GitHub repository**.

---

## ⚙️ Requirements
- **Python 3.9+**
- Core dependencies:
  - `tensorflow`
  - `pandas`
  - `numpy`
  - `scikit-learn`
  - `statsmodels`
  - `requests`
  - `PyGithub`

---

## 📥 Installation
Clone the repository and install the dependencies:

```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>
pip install -r requirements.txt
```

⚠️ Make sure you have a valid **GitHub Personal Access Token** configured inside `connections.py` in order to push updates to your repository.

---

## ▶️ Usage
Run the main application:

```bash
python main.py
```

The program will:
1. Load token configurations and historical price data.
2. Train the LSTM/BiLSTM model for each token.
3. Predict upcoming prices (daily, weekly, monthly, yearly).
4. Save the predictions into `result.csv`.
5. Push the results to the specified GitHub repository.

---

## 📂 Project Structure
```
.
├── main.py               # Application entry point
├── cryptocurrency.py     # Core price prediction logic
├── connections.py        # GitHub connection and file updating
├── utils.py              # Utility helpers (Token, Utils classes, etc.)
├── TOKENCONFIGS.csv      # Token configuration file
├── result.csv            # Generated predictions
├── token-history/        # Folder where historical token data is stored
```

---

## ⚡ How It Works
1. **Token Configuration**  
   The app reads tokens and their intervals from `TOKENCONFIGS.csv`.  
   For example, if a token is set with a daily interval, its data will be downloaded and updated once per day.

2. **Data Fetching & Storage**  
   - For each token, historical price data is fetched from the internet.  
   - Data is automatically saved inside the `token-history` folder in CSV format.  
   - Each file follows the naming pattern:  
     ```
     <TOKEN_NAME>_<INTERVAL>.csv
     ```

3. **Data Cleaning**  
   Historical prices are processed through an **Isolation Forest** to remove outliers (e.g., sudden anomalies, incorrect spikes).

4. **Model Training**  
   - A TensorFlow/Keras **LSTM + BiLSTM** network is built.  
   - Training parameters (units, epochs, timesteps, batch size) are automatically adjusted for each interval.  

5. **Prediction**  
   - The model predicts the next **high/low prices** for each token.  
   - Forecast horizons include: today, tomorrow, week, month, year.  

6. **Result Handling**  
   - Predictions are written into `result.csv`.  
   - The app pushes the updated results into a GitHub repository (configured in `connections.py`).  

---

## 🤝 Contributing
Contributions, issues, and feature requests are welcome!  
To contribute:
1. Fork this repo.
2. Create a feature branch (`git checkout -b feature/new-feature`).
3. Commit your changes (`git commit -m 'Add new feature'`).
4. Push to your branch (`git push origin feature/new-feature`).
5. Open a Pull Request.

---

## 📜 License
Distributed under the **MIT License**. See `LICENSE` for more information.

---

## 📧 Contact
Created by **alireza-py**
