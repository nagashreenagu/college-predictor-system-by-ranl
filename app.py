import pickle
from flask import Flask, request, render_template
import numpy as np # type: ignore
import gspread # pyright: ignore[reportMissingImports]

app = Flask(__name__)

# Load the model
try:
    model = pickle.load(open("model1.pkl", "rb"))
except Exception as e:
    print("Warning: Could not load model:", e)

# Home route
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')  

@app.route('/colleges')
def colleges():
    return render_template('Top Colleges.html')     

@app.route('/learn')
def learn():
    return render_template('Coding.html')     

@app.route('/support')
def support():
    return render_template('support.html')   

@app.route('/faq')
def faq():
    return render_template('faq.html')              

# Prediction route
@app.route('/predict', methods=['POST'])
def predict():
    # Dictionaries for mapping
    Category = {
        '0':'General', '1':'Other Backward Classes-Non Creamy Layer', '6':'Scheduled Castes',
        '8':'Scheduled Tribes','3':'General & Persons with Disabilities', 
        '5':'Other Backward Classes & Persons with Disabilities', 
        '7':'Scheduled Castes & Persons with Disabilities', 
        '9':'Scheduled Tribes & Persons with Disabilities',
        '1':'General & Economically Weaker Section', 
        '2':'General & Economically Weaker Section & Persons with Disability'
    }
    
    Quota = {'0':'All-India', '3':'Home-State', '1':'Andhra Pradesh', '2':'Goa', '4':'Jammu & Kashmir', '5':'Ladakh'}
    Pool = {'0':'Neutral', '1':'Female Only'}
    Institute = {'0':'IIT', '1':'NIT'}

    # Connect to Google Sheets
    sa = gspread.service_account(filename="College.json")
    sh = sa.open("College Data")
    wks = sh.worksheet("Sheet1")

    # Get form data
    data = [x for x in request.form.values()]
    list1 = data.copy()

    # Map coded values to readable form
    list1[2] = Category.get(list1[2])
    list1[3] = Quota.get(list1[3])
    list1[4] = Pool.get(list1[4])
    list1[5] = Institute.get(list1[5])

    # Prepare numeric data for prediction
    data.pop(0)  # remove name or text input if needed
    data.pop(0)
    data.pop(7)  # adjust if necessary
    data1 = [float(x) for x in data]

    final_input = np.array(data1).reshape(1, -1)
    output = model.predict(final_input)[0]

    # Append prediction to Google Sheet
    list1.extend(output)  # assuming output is a list/tuple of 3 values
    wks.append_row(list1, table_range="A2:M2")

    return render_template(
        "home.html",
        prediction_text="College : {} , Degree : {} , Course : {}".format(output[0], output[1], output[2]),
        prediction="Thank you, Hope this will match your requirement !!!"
    )

if __name__ == '__main__':
    app.run(debug=True)
