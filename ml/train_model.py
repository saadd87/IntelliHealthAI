import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib


# Load Dataset
data = pd.read_csv('dataset.csv')

# Features
X = data[['age', 'weight', 'height', 'bp', 'glucose']]

# Target
y = data['risk']

# Split Data
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# Create Model
model = RandomForestClassifier()

# Train Model
model.fit(X_train, y_train)

# Prediction
predictions = model.predict(X_test)

# Accuracy
accuracy = accuracy_score(y_test, predictions)

print("Accuracy:", accuracy)

# Save Model
joblib.dump(model, 'health_model.pkl')

print("Model Saved Successfully")