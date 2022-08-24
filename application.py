from flask import Flask, redirect, url_for, request, render_template
import datetime
import pandas as pd
app = Flask(__name__)
 

def calc(date):
    """
    input: study permit application date
    output: most probable date for PPR, probability of getting PPR on the very next working day 
    """
    df = pd.read_csv('VisaPPR.csv', parse_dates=['result_date', 'app_date'])
    df['processing_days'] = (df['result_date'] - df['app_date']).apply(lambda x: x.days)
    med = df['processing_days'].median()
    date = pd.to_datetime(date)
    days = datetime.datetime.today() - date
    days = days.days
    prob = len(df[df['processing_days']<=days])/len(df)
    if days > med:
        med = df[df['processing_days']>=days]['processing_days'].median()
    result_date = date + datetime.timedelta(days=med)
    result_date = result_date.strftime('%d %B %Y')
    if prob > 0.5:
        result_date = 'the next working day of IRCC'
    return result_date, prob

 
@app.route('/', methods=['POST', 'GET'])
def fun():
    return render_template('index.html')


@app.route('/success', methods=['POST', 'GET'])
def success():
    if request.method == 'POST':
        date = request.form['date']
        prob = request.form['prob']
    else:
        date = request.args.get('date')
        prob = request.args.get('prob')
    assurance = ''
    if(float(prob)<0.05):
        assurance = "<h1>It is just a dumb predictor don't take it seriously, you will get your PPR on time</h1>"
    output = '''<div style="text-align:center"><h1>You have a %.2f percent chance of getting PPR on the next working day of IRCC</h1>
            </br>
            <h1>You will most likely get your VISA before %s there is a 50 percent chance of that</h1>
            </br>
            '''+assurance+'''
            </div>'''
    return  output% (100*float(prob), date)
 
 
@app.route('/index', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        date = request.form['date']
        result_date, prob = calc(date)
        return redirect(url_for('success', date=result_date, prob=prob))
    else:
        date = request.args.get('date')
        result_date, prob = calc(date)
        return redirect(url_for('success', date=result_date, prob=prob))
 
 
if __name__ == '__main__':
    app.run(debug=True)