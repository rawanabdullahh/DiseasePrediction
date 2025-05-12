from flask import Flask, request, jsonify, render_template
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import uuid
import warnings
import logging
import os
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Load datasets
def load_data():
    try:
        # Verify file existence
        comb_file = 'dis_sym_dataset_comb.csv'
        details_file = 'disease_details (1).csv'

        if not os.path.exists(comb_file):
            logger.error(f"Symptom dataset file not found: {comb_file}")
            raise FileNotFoundError(f"File not found: {comb_file}")
        if not os.path.exists(details_file):
            logger.error(f"Prevention details file not found: {details_file}")
            raise FileNotFoundError(f"File not found: {details_file}")

        logger.info("Loading symptom-disease dataset")
        df = pd.read_csv(comb_file)
        logger.info(f"Loaded symptom-disease dataset with shape: {df.shape}")

        # Remove duplicate rows
        df = df.drop_duplicates(subset=df.columns, keep='first')
        logger.info(f"Dataset after removing duplicates: {df.shape}")

        logger.info("Loading prevention tips dataset")
        prevention_df = pd.read_csv(details_file)
        logger.info(f"Loaded prevention dataset with shape: {prevention_df.shape}")

        # Validate required columns
        if 'label_dis' not in df.columns:
            logger.error("Missing 'label_dis' column in symptom dataset")
            raise ValueError("Missing 'label_dis' column in symptom dataset")
        if 'Disease' not in prevention_df.columns or 'Prevention_Tip' not in prevention_df.columns:
            logger.error("Missing required columns in prevention dataset")
            raise ValueError("Missing 'Disease' or 'Prevention_Tip' column in prevention dataset")

        # Clean prevention data
        prevention_df['Disease'] = prevention_df['Disease'].str.strip().str.lower()
        prevention_dict = dict(zip(prevention_df['Disease'], prevention_df['Prevention_Tip']))

        return df, prevention_dict
    except Exception as e:
        logger.error(f"Error loading data: {str(e)}")
        return None, None

# Preprocess data and train model
def prepare_model(df):
    try:
        logger.info("Preparing model")

        # Extract features (symptoms) and labels (diseases)
        X = df.drop('label_dis', axis=1)
        y = df['label_dis']

        # Validate data
        if X.empty or y.empty:
            logger.error("Empty feature or label data")
            raise ValueError("Empty feature or label data")

        # Handle missing values
        X = X.fillna(0)

        # Verify all columns are numeric
        non_numeric_cols = X.select_dtypes(exclude=[np.number]).columns
        if len(non_numeric_cols) > 0:
            logger.error(f"Non-numeric columns found: {non_numeric_cols}")
            raise ValueError(f"Non-numeric columns: {non_numeric_cols}")

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        logger.info(f"Training set shape: {X_train.shape}, Test set shape: {X_test.shape}")

        # Train Random Forest model
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)

        # Evaluate model
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        logger.info(f"Model accuracy: {accuracy:.2f}")

        return model, X.columns
    except Exception as e:
        logger.error(f"Error preparing model: {str(e)}")
        return None, None

# Load data and model on startup
logger.info("Starting application")
df, prevention_dict = load_data()
if df is not None:
    model, symptom_columns = prepare_model(df)
else:
    model, symptom_columns = None, None
    logger.error("Failed to initialize model or symptom columns")

# Root route to render the front-end
@app.route('/')
def index():
    return render_template('index.html')

# Predict endpoint
@app.route('/predict', methods=['POST'])
def predict():
    if model is None or symptom_columns is None:
        logger.error("Predict endpoint called but model or symptom columns are not loaded")
        return jsonify({
            'error': 'Model or data not loaded properly'
        }), 500

    try:
        # Get symptoms from request
        data = request.get_json()
        logger.debug(f"Received payload: {data}")
        user_symptoms = data.get('symptoms', [])

        if not user_symptoms:
            logger.warning("No symptoms provided in request")
            return jsonify({
                'error': 'No symptoms provided'
            }), 400

        # Create symptom vector
        symptom_vector = np.zeros(len(symptom_columns))
        user_symptoms = [s.strip().lower() for s in user_symptoms]
        logger.debug(f"Processed symptoms: {user_symptoms}")

        unrecognized_symptoms = []
        for symptom in user_symptoms:
            if symptom in symptom_columns:
                symptom_vector[list(symptom_columns).index(symptom)] = 1
            else:
                unrecognized_symptoms.append(symptom)
                logger.warning(f"Symptom not found in dataset: {symptom}")

        if unrecognized_symptoms:
            logger.info(f"Unrecognized symptoms: {unrecognized_symptoms}")

        logger.debug(f"Symptom vector: {symptom_vector[:10]}... (first 10 elements)")

        # Predict probabilities
        probabilities = model.predict_proba([symptom_vector])[0]
        disease_probs = list(zip(model.classes_, probabilities))

        # Sort by probability and filter low probabilities
        disease_probs = sorted(disease_probs, key=lambda x: x[1], reverse=True)
        disease_probs = [(d, p) for d, p in disease_probs if p > 0.001][:10]  # Threshold: 0.1%

        # Prepare response
        results = []
        for disease, prob in disease_probs:
            disease_clean = disease.strip().lower()
            result = {
                'disease': disease,
                'probability': round(float(prob) * 100, 2),
                'prevention_tip': prevention_dict.get(disease_clean, 'No prevention tip available')
            }
            results.append(result)

        response = {
            'predictions': results,
            'request_id': str(uuid.uuid4())
        }
        logger.info(f"Prediction successful, returning {len(results)} results")
        return jsonify(response)
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        return jsonify({
            'error': f'Prediction error: {str(e)}'
        }), 500

# Symptoms endpoint
@app.route('/symptoms', methods=['GET'])
def get_symptoms():
    if symptom_columns is None:
        logger.error("Symptoms endpoint called but symptom columns are not loaded")
        return jsonify({
            'error': 'Symptom data not loaded'
        }), 500

    response = {
        'symptoms': list(symptom_columns),
        'request_id': str(uuid.uuid4())
    }
    logger.info("Returning symptom list")
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)