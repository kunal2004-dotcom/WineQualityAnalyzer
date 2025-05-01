import streamlit as st
import pandas as pd
import numpy as np
import pickle
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# Set page configuration
st.set_page_config(
    page_title="Wine Quality Prediction",
    page_icon="🍷",
    layout="wide"
)

# Title and description
st.title("Wine Quality Prediction")
st.markdown("This application predicts the quality of wine based on physicochemical properties.")

# Sidebar for navigation
page = st.sidebar.selectbox("Choose a page", ["Prediction", "Data Exploration", "Model Information"])

# Load the dataset
@st.cache_data
def load_data():
    wine_dataset = pd.read_csv('winequality-red.csv')
    return wine_dataset

# Train the model
@st.cache_resource
def train_model(wine_dataset):
    # Data preprocessing
    X = wine_dataset.drop('quality', axis=1)
    Y = wine_dataset['quality'].apply(lambda y_value: 1 if y_value>=7 else 0)
    
    # Train test split
    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=3)
    
    # Model training
    model = RandomForestClassifier()
    model.fit(X_train, Y_train)
    
    # Accuracy calculation
    X_test_prediction = model.predict(X_test)
    test_data_accuracy = accuracy_score(X_test_prediction, Y_test)
    
    return model, test_data_accuracy, X.columns

# Load data and train model
wine_dataset = load_data()
model, accuracy, feature_names = train_model(wine_dataset)

# Prediction page
if page == "Prediction":
    st.header("Wine Quality Prediction")
    st.write("Enter the characteristics of your wine to predict its quality.")
    
    # Create two columns for input fields
    col1, col2 = st.columns(2)
    
    with col1:
        fixed_acidity = st.slider("Fixed Acidity", float(wine_dataset["fixed acidity"].min()), float(wine_dataset["fixed acidity"].max()), float(wine_dataset["fixed acidity"].mean()))
        volatile_acidity = st.slider("Volatile Acidity", float(wine_dataset["volatile acidity"].min()), float(wine_dataset["volatile acidity"].max()), float(wine_dataset["volatile acidity"].mean()))
        citric_acid = st.slider("Citric Acid", float(wine_dataset["citric acid"].min()), float(wine_dataset["citric acid"].max()), float(wine_dataset["citric acid"].mean()))
        residual_sugar = st.slider("Residual Sugar", float(wine_dataset["residual sugar"].min()), float(wine_dataset["residual sugar"].max()), float(wine_dataset["residual sugar"].mean()))
        chlorides = st.slider("Chlorides", float(wine_dataset["chlorides"].min()), float(wine_dataset["chlorides"].max()), float(wine_dataset["chlorides"].mean()))
        free_sulfur_dioxide = st.slider("Free Sulfur Dioxide", float(wine_dataset["free sulfur dioxide"].min()), float(wine_dataset["free sulfur dioxide"].max()), float(wine_dataset["free sulfur dioxide"].mean()))
    
    with col2:
        total_sulfur_dioxide = st.slider("Total Sulfur Dioxide", float(wine_dataset["total sulfur dioxide"].min()), float(wine_dataset["total sulfur dioxide"].max()), float(wine_dataset["total sulfur dioxide"].mean()))
        density = st.slider("Density", float(wine_dataset["density"].min()), float(wine_dataset["density"].max()), float(wine_dataset["density"].mean()))
        pH = st.slider("pH", float(wine_dataset["pH"].min()), float(wine_dataset["pH"].max()), float(wine_dataset["pH"].mean()))
        sulphates = st.slider("Sulphates", float(wine_dataset["sulphates"].min()), float(wine_dataset["sulphates"].max()), float(wine_dataset["sulphates"].mean()))
        alcohol = st.slider("Alcohol", float(wine_dataset["alcohol"].min()), float(wine_dataset["alcohol"].max()), float(wine_dataset["alcohol"].mean()))
    
    # Create a button for prediction
    if st.button("Predict Wine Quality"):
        # Create input array for prediction
        input_data = np.array([fixed_acidity, volatile_acidity, citric_acid, residual_sugar, 
                              chlorides, free_sulfur_dioxide, total_sulfur_dioxide, 
                              density, pH, sulphates, alcohol]).reshape(1, -1)
        
        # Make prediction
        prediction = model.predict(input_data)
        prediction_proba = model.predict_proba(input_data)
        
        # Display result
        st.subheader("Prediction Result")
        if prediction[0] == 1:
            st.success("Good Quality Wine! 🍷")
        else:
            st.warning("Bad Quality Wine! ⚠️")
        
        # Display probability
        st.write(f"Confidence: {prediction_proba[0][prediction[0]]:.2%}")
        
        # Display feature importance for this prediction
        st.subheader("Feature Importance for This Prediction")
        feature_importance = pd.DataFrame({
            'Feature': feature_names,
            'Importance': model.feature_importances_
        }).sort_values('Importance', ascending=False)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(x='Importance', y='Feature', data=feature_importance, palette='viridis')
        plt.title('Feature Importance for Wine Quality')
        st.pyplot(fig)

# Data Exploration page
elif page == "Data Exploration":
    st.header("Data Exploration")
    
    # Display dataset info
    st.subheader("Dataset Information")
    st.write(f"Dataset Shape: {wine_dataset.shape}")
    st.write(f"Number of Good Quality Wines (Quality >= 7): {len(wine_dataset[wine_dataset['quality'] >= 7])}")
    st.write(f"Number of Bad Quality Wines (Quality < 7): {len(wine_dataset[wine_dataset['quality'] < 7])}")
    
    # Display the dataset
    st.subheader("Dataset Preview")
    st.dataframe(wine_dataset.head())
    
    # Display statistics
    st.subheader("Statistical Summary")
    st.dataframe(wine_dataset.describe())
    
    # Visualizations
    st.subheader("Visualizations")
    
    # Quality distribution
    st.write("### Quality Distribution")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.countplot(x='quality', data=wine_dataset, palette='viridis')
    plt.title('Distribution of Wine Quality')
    plt.xlabel('Quality')
    plt.ylabel('Count')
    st.pyplot(fig)
    
    # Correlation heatmap
    st.write("### Correlation Heatmap")
    correlation = wine_dataset.corr()
    fig, ax = plt.subplots(figsize=(12, 10))
    sns.heatmap(correlation, cbar=True, square=True, fmt='.1f', annot=True, annot_kws={'size':8}, cmap='Blues')
    plt.title('Correlation Between Features')
    st.pyplot(fig)
    
    # Feature vs Quality plots
    st.write("### Feature vs Quality Relationships")
    feature = st.selectbox("Select Feature to Visualize", wine_dataset.drop('quality', axis=1).columns)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x='quality', y=feature, data=wine_dataset, palette='viridis')
    plt.title(f'{feature} vs Quality')
    plt.xlabel('Quality')
    plt.ylabel(feature)
    st.pyplot(fig)

# Model Information page
elif page == "Model Information":
    st.header("Model Information")
    
    st.subheader("Model Performance")
    st.write(f"Model Accuracy: {accuracy:.2%}")
    
    st.subheader("Feature Importance")
    feature_importance = pd.DataFrame({
        'Feature': feature_names,
        'Importance': model.feature_importances_
    }).sort_values('Importance', ascending=False)
    
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.barplot(x='Importance', y='Feature', data=feature_importance, palette='viridis')
    plt.title('Feature Importance for Wine Quality')
    st.pyplot(fig)
    
    st.subheader("Model Details")
    st.write("This application uses a Random Forest Classifier to predict wine quality.")
    st.write("The model classifies wines as either 'Good Quality' (quality score >= 7) or 'Bad Quality' (quality score < 7).")
    st.write("The model was trained on the Red Wine Quality dataset, which contains various physicochemical properties of wines.")