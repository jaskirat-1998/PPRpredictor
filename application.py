from flask import Flask, redirect, url_for, request, render_template, json
import datetime
import pandas as pd
app = Flask(__name__)
 

def get_cdf(days,  df):
    """
    input: study permit application date and dataframe with past PPR's data
    output: data to plot cumulative probability distribution
    """
    dates = []
    probs = []
    l = len(df)
    present_date = datetime.datetime.today().date()
    for i in range(1,11):
        days+=1
        l1 = len(df[df['processing_days']<=days])
        probs.append(round(l1/l,2))
        date_ = present_date + datetime.timedelta(days=i)
        dates.append( date_.strftime('%d %B %Y'))
    return dates, probs

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
    dates, probs = get_cdf(days,  df)
    prob = len(df[df['processing_days']<=days])/len(df)
    if days > med:
        med = df[df['processing_days']>=days]['processing_days'].median()
    result_date = date + datetime.timedelta(days=med)
    result_date = result_date.strftime('%d %B %Y')
    if prob > 0.5:
        result_date = 'the next working day of IRCC'
    return result_date, round(100*prob,2), dates, probs

 
@app.route('/', methods=['POST', 'GET'])
def fun():
    return render_template('index.html')


@app.route('/success', methods=['POST', 'GET'])
def success():
    if request.method == 'POST':
        date = request.form['date']
        result_date, prob, dates, probs = calc(date)
    else:
        date = request.args.get('date')
        result_date, prob, dates, probs = calc(date)
    return render_template('success.html', prob=prob, dates=dates, probs=probs)
 
 
@app.route('/index', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        date = request.form['date']
        result_date, prob, dates, probs = calc(date)
        return render_template('success.html', prob=prob, dates=dates, probs=probs)
        #return redirect(url_for('success', date=date))
    else:
        date = request.args.get('date')
        result_date, prob, dates, probs = calc(date)
        return render_template('success.html', prob=prob, dates=dates, probs=probs)
        #return redirect(url_for('success', date=date))
 
 
if __name__ == '__main__':
    app.run(debug=True)