from flask import Flask, request, jsonify, render_template
import pandas as pd
import numpy as np
import json

app = Flask(__name__)
df = pd.read_csv(r"D:\decsion_tree\lifeexpectancy\newdata.csv")

def convert_to_vector(input_dict):
    response_mapping = {
        "never": 0,
        "rarely": 0.2514,
        "slightly": 0.2514,
        "sometimes": 0.7486,
        "moderately": 0.7486,
        "frequently": 1,
        "regularly": 1,
        "yes": 1,
        "no": 0
    }

    output_vector = []
    for value in input_dict.values():
        normalized_value = value.lower().split()[0]
        if normalized_value in response_mapping:
            output_vector.append(response_mapping[normalized_value])
        else:
            raise ValueError(f"Unrecognized response: {value}")
    return output_vector

def calculate_lifespan_change(input_dict, gender):

    input_vector = convert_to_vector(input_dict)

    if len(input_vector) != len(df):
        raise ValueError(f"Input vector must have {len(df)} elements, one for each factor.")

    if gender.lower() not in ['male', 'female']:
        raise ValueError("Gender must be either 'male' or 'female'.")

    total_change = 0
    for i, (years, affected) in enumerate(zip(df['Years gained / lost'], df['Sexes affected'])):
        if (gender == 'male' and affected.lower() != 'female') or \
                (gender == 'female' and affected.lower() != 'male'):
            total_change += years * input_vector[i]

    return total_change / 6

def estimated_age(input_dict, gender):
    average_age = 75
    change_in_age = calculate_lifespan_change(input_dict, gender)
    return int(average_age + change_in_age), change_in_age

def report(input_dict, gender):
    estimated_lifespan, change_in_age = estimated_age(input_dict, gender)

    gender_mask = ((gender == 'male') & (df['Sexes affected'].str.lower() != 'female')) | \
                  ((gender == 'female') & (df['Sexes affected'].str.lower() != 'male'))

    impact = df['Years gained / lost'] * np.array(list(convert_to_vector(input_dict))) * gender_mask

    factors = df[impact != 0].copy()
    factors['Adjusted Impact'] = impact[impact != 0]
    factors = factors.sort_values('Adjusted Impact', key=abs, ascending=False)

    factors_list = []
    for _, row in factors.iterrows():
        factor = row['Factor']
        full_impact = row['Years gained / lost']
        adjusted_impact = row['Adjusted Impact']
        percentage = (adjusted_impact / full_impact) * 100

        factors_list.append({
            "factor": factor,
            "impact": round(adjusted_impact, 2),
            "percentage_of_full_impact": round(percentage, 1)
        })

    output = {
        "gender": gender,
        "estimated_lifespan": estimated_lifespan,
        "change_in_age": round(change_in_age, 2),
        "factors": factors_list,
        "recommendation": "To improve your health further, we recommend fully adopting positive lifestyle habits and addressing the negative factors listed above."
    }

    return json.dumps(output, indent=2)

@app.route('/')
def index():
    questions = df['Factor'].tolist()
    return render_template('index.html', questions=questions)

@app.route('/calculate', methods=['POST'])
def calculate():
    input_dict = request.form.to_dict()  # Capture user inputs from the form
    gender = input_dict.pop('gender')  # Get the gender from the form
    result = report(input_dict, gender)  # Generate the report

    return jsonify(result)  # Return JSON response with the report

if __name__ == '__main__':
    app.run(debug=True)
