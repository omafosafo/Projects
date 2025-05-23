# Import Dependencies
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.svm import SVC
from sklearn import metrics

# Load Data
data = pd.read_csv('risk_factors_cervical_cancer.csv')

# Clean Column Names
data.columns = data.columns.str.replace(' ', '_').str.lower()

# Replace '?' and empty strings with NaN
data = data.replace(['?', ''], np.nan)

# Drop rows with missing values
data = data.dropna()

# Check for and drop duplicates
data = data.drop_duplicates()

# Select continuous features and target variable
features = ['age', 'stds:_number_of_diagnosis', 'dx:cancer',
            'dx:cin', 'dx:hpv', 'dx',
            'hinselmann', 'schiller', 'citology']
target = 'biopsy'

X = data[features]
y = data[target].astype(int)  # Ensure the target is integer

# Impute missing values with median (for robustness)
imputer = SimpleImputer(strategy="median")
X_imputed = imputer.fit_transform(X)

# Train-Test Split (70-30)
X_train, X_test, y_train, y_test = train_test_split(
    X_imputed, y, test_size=0.3, random_state=42, shuffle=True
)

# Standardize Features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Hyperparameter Tuning: Try multiple SVM kernels
param_grid = [{'kernel': ['linear', 'rbf', 'poly', 'sigmoid']}]
gs = GridSearchCV(SVC(probability=True, gamma='scale'), param_grid, cv=5, scoring='roc_auc')
gs.fit(X_train_scaled, y_train)

# Best Parameters
print(f"Best Kernel: {gs.best_params_['kernel']}")

# Predictions
y_probs = gs.predict_proba(X_test_scaled)[:, 1]
y_pred = gs.predict(X_test_scaled)

# Evaluation Metrics
print("\nModel Performance Metrics:")
print("AUC Score: ", metrics.roc_auc_score(y_test, y_probs))
print("F1 Score: ", metrics.f1_score(y_test, y_pred))
print("Precision: ", metrics.precision_score(y_test, y_pred))
print("Recall: ", metrics.recall_score(y_test, y_pred))
print("Balanced Accuracy: ", metrics.balanced_accuracy_score(y_test, y_pred))

# Optional: Full classification report
print("\nClassification Report:")
print(metrics.classification_report(y_test, y_pred))
