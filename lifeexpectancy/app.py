from flask import Flask, request, jsonify, render_template
import pandas as pd
import numpy as np

app = Flask(__name__)

# Load the dataset
df = pd.read_csv("LiveLongerData.csv")
df = df.drop(columns=["strength of science?", "effect", "Comment", "Note", "ID", "Sources", "Links"])

def calculate_lifespan_change(input_vector, gender):
    if len(input_vector) != len(df):
        raise ValueError(f"Input vector must have {len(df)} elements, one for each factor.")

    if gender.lower() not in ['male', 'female']:
        raise ValueError("Gender must be either 'male' or 'female'.")

    total_change = 0
    for i, (years, affected) in enumerate(zip(df['Years gained / lost'], df['sexes affected'])):
        if (gender == 'male' and affected.lower() != 'female') or \
                (gender == 'female' and affected.lower() != 'male'):
            total_change += years * input_vector[i]

    return total_change/4

def estimated_age(input_vector, gender):
    average_age = 75
    change_in_age = calculate_lifespan_change(input_vector, gender)
    return int(average_age + change_in_age), change_in_age

@app.route('/')
def index():
    questions = df['Factor'].tolist()
    return render_template('index.html', questions=questions)

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.json
    input_vector = data['input_vector']
    gender = data['gender']

    try:
        estimated_lifespan, change_in_age = estimated_age(input_vector, gender)

        negative_factors = []
        positive_factors = []

        for i, (factor, years, affected) in enumerate(zip(df['Factor'], df['Years gained / lost'], df['sexes affected'])):
            if input_vector[i] == 1:
                if (gender == 'male' and affected.lower() != 'female') or (gender == 'female' and affected.lower() != 'male'):
                    if years < 0:
                        negative_factors.append(f"{factor}: {years} years")
                    else:
                        positive_factors.append(f"{factor}: +{years} years")

        if change_in_age > 0:
            extra_years = f"You're expected to live {change_in_age:.2f} extra years compared to the average life expectancy."
        elif change_in_age < 0:
            extra_years = f"You're expected to live {abs(change_in_age):.2f} fewer years compared to the average life expectancy."
        else:
            extra_years = "You're expected to live exactly the average life expectancy."

        return jsonify({
            'estimated_lifespan': estimated_lifespan,
            'extra_years': extra_years,
            'negative_factors': negative_factors,
            'positive_factors': positive_factors
        })

    except ValueError as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)