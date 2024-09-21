import numpy as np
import pandas as pd

# Load the dataset
df = pd.read_csv(r"LiveLongerData.csv")
df = df.drop(columns=["strength of science?", "effect", "Comment", "Note", "ID", "Sources", "Links"])


def print_dataset(arg):
    pd.set_option('display.max_columns', None)  # Show all columns
    pd.set_option('display.width', 1000)  # Set the display width to prevent column wrapping
    pd.set_option('display.max_colwidth', None)  # Ensure columns with long text are not truncated
    df = arg
    print(df)


def calculate_lifespan_change(input_vector, gender):
    """
    Calculates the change in life expectancy based on the user's input.
    :param input_vector: List of binary responses (1 for 'yes', 0 for 'no') to lifestyle questions.
    :param gender: The gender of the user ('male' or 'female').
    :return: Total change in lifespan.
    """
    if len(input_vector) != len(df):
        raise ValueError(f"Input vector must have {len(df)} elements, one for each factor.")

    if gender.lower() not in ['male', 'female']:
        raise ValueError("Gender must be either 'male' or 'female'.")

    # Calculate the total lifespan change based on gender and factor impact
    total_change = 0
    for i, (years, affected) in enumerate(zip(df['Years gained / lost'], df['sexes affected'])):
        # Apply gender filter for affected categories
        if (gender == 'male' and affected.lower() != 'female') or \
                (gender == 'female' and affected.lower() != 'male'):
            total_change += years * input_vector[i]

    return total_change/4


def get_user_input():
    """
    Gathers user responses to lifestyle questions and asks for gender.
    :return: A tuple containing the input_vector (list of binary responses) and gender.
    """
    questions = [
        "Do you smoke regularly?", "Do you spend long periods of time sitting each day?",
        "Do you often sleep for more than 9 hours a night?", "Would you describe yourself as an optimistic person?",
        "Do you own pets or spend time with animals regularly?",
        "Do you have a high level of professional responsibility or stress at work?",
        "Do you maintain a balanced and healthy diet?", "Do you frequently eat red meat?",
        "Do you consume alcohol in excessive amounts frequently?", "Do you live in a city or urban environment?",
        "Have you been diagnosed with a mental illness?", "Do you consider yourself overweight or obese?",
        "Do you get regular health check-ups or screenings?",
        "Do you live or spend a significant amount of time at high altitudes?",
        "Are you in a happy or healthy marriage?",
        "Do you intentionally eat smaller portions of food to maintain or reduce weight?",
        "Do you meditate regularly?", "Do you actively take steps to prevent heart disease?",
        "Do you maintain a lifestyle that includes non-smoking, regular exercise, and healthy eating?",
        "Do you spend significant time in the company of women?",
        "Do you take preventive measures to reduce your risk of cancer?",
        "Do you exercise regularly?", "Do you occasionally drink alcohol in moderation?",
        "Would you describe yourself as conscientious and emotionally stable?",
        "Do you experience regular sexual activity or orgasms?",
        "Do you occasionally drink a small amount of wine?",
        "Do you have a high level of financial security or income?",
        "Are you a woman?", "Do you have a close group of friends with whom you regularly spend time?",
        "Do you regularly attend religious services or have a strong faith?",
        "Do you live in a rural or country environment?",
        "Do you practice or believe in polygamy?",
        "Do you believe you have a strong family history of good health or longevity?",
        "Do you engage in light exercise or physical activity?", "Do you own or regularly interact with dogs?"
    ]

    print("Please answer the following questions about your lifestyle:")
    input_vector = []

    # Ask each question and collect the response
    for question in questions:
        while True:
            response = input(f"{question} (yes/no): ").lower()
            if response in ['yes', 'no']:
                input_vector.append(1 if response == 'yes' else 0)
                break
            else:
                print("Please answer with 'yes' or 'no'.")

    # Ask for gender
    while True:
        gender = input("What is your gender? (male/female): ").lower()
        if gender in ['male', 'female']:
            break
        else:
            print("Please enter either 'male' or 'female'.")

    return input_vector, gender


def estimated_age(input_vector, gender):
    """
    Estimates the user's life expectancy based on their lifestyle choices and gender.
    :param input_vector: List of binary responses to the lifestyle questions.
    :param gender: The gender of the user.
    :return: Estimated age (life expectancy).
    """
    average_age = 75  # Assuming a baseline average life expectancy of 75 years
    change_in_age = calculate_lifespan_change(input_vector, gender)
    return int(average_age + change_in_age), change_in_age


def report(input_vector, gender):
    """
    Generates a report based on the user's input and provides a life expectancy estimate,
    including factors that positively or negatively impacted the user's lifespan.
    """
    estimated_lifespan, change_in_age = estimated_age(input_vector, gender)

    # Find factors that positively or negatively affected the user
    negative_factors = []
    positive_factors = []

    for i, (factor, years, affected) in enumerate(zip(df['Factor'], df['Years gained / lost'], df['sexes affected'])):
        if input_vector[i] == 1:  # If the user answered 'yes' to this factor
            if (gender == 'male' and affected.lower() != 'female') or (
                    gender == 'female' and affected.lower() != 'male'):
                if years < 0:
                    negative_factors.append(f"{factor}: {years} years")
                else:
                    positive_factors.append(f"{factor}: +{years} years")

    # Report the number of extra years (or fewer years) the person is expected to live
    if change_in_age > 0:
        extra_years = f"You're expected to live {change_in_age:.2f} extra years compared to the average life expectancy."
    elif change_in_age < 0:
        extra_years = f"You're expected to live {abs(change_in_age):.2f} fewer years compared to the average life expectancy."
    else:
        extra_years = "You're expected to live exactly the average life expectancy."

    print(f"""
    Based on your responses and your gender ({gender}), we estimate that your life expectancy will be {estimated_lifespan} years.

    {extra_years}

    Factors that negatively affected your life expectancy:
    {', '.join(negative_factors) if negative_factors else 'None'}

    Factors that positively affected your life expectancy:
    {', '.join(positive_factors) if positive_factors else 'None'}

    To improve your health further, we recommend continuing with the positive lifestyle habits and addressing the negative factors listed above.
    """)


# Example usage:
input_vector, gender = get_user_input()  # Gather user input
report(input_vector, gender)  # Generate the report based on input
