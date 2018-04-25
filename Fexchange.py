from flask import Flask, request, jsonify , send_file , render_template, redirect 
import requests
import datetime as DT
import matplotlib
matplotlib.use('Agg') # choosing Agg backend as Tkinter was giving errors(must be done before importing pyplot)
import matplotlib.pyplot as plt


app=Flask(__name__)


url="https://exchangeratesapi.io/api"

def graphGenerator(data):
	data=data.json()
	base=data.get('base')
	date=data.get('date')
	rates=data.get('rates')
	rates=sorted(rates.items(), key=lambda x: x[1])
	x1=list()
	y1=list()
	x2=list()
	y2=list()
	length=len(rates)
	for i in range(length):
		if i >length//2:
			x2.append(rates[i][0])
			y2.append(rates[i][1])
		else:
			x1.append(rates[i][0])
			y1.append(rates[i][1])
	x1.insert(0,base)
	x2.insert(0,base)
	y1.insert(0,1)
	y2.insert(0,1)
	plt.figure(figsize=(15,8))
	plt.style.use('dark_background')
	plt.subplot(211)
	plt.plot(x1,y1,color='blue',marker='o', markerfacecolor='white', markersize=5)
	for xy in zip(x1, y1):                                       
		plt.annotate('%.3f' % xy[1], xy=xy) ## labelling coordinates
	plt.fill_between(x1,y1, color='blue', alpha='0.3') ##filling under the lines
	plt.ylabel(base,color='white')
	plt.title('EXCHANGE RATE AS OF '+date,color='white')

	#second graph
	plt.subplot(212)
	plt.plot(x2,y2,color='red',marker='o', markerfacecolor='white', markersize=5)
	for xy in zip(x2, y2):                                       
		plt.annotate('%.3f' % xy[1], xy=xy)
	plt.fill_between(x2,y2, color='red', alpha='0.3')
	plt.xlabel('CURRENCIES',color='white')
	plt.ylabel(base,color='white')

	plt.savefig('fig.png', dpi=300)
	plt.close()
	return None

@app.route('/')
def Main():
	return render_template('home.html')

@app.route('/readme')
def readme():
	return render_template('readme.html')

@app.route('/docLatest',methods=['GET', 'POST'])
def exchange():
	if request.method == 'GET':
		return render_template('docLatest.html')
	elif request.method == 'POST':
		base=request.form.get('base')
		base=base.strip()
		tempurl=url+'/latest'
		data=requests.get(tempurl,params={'base':base})
		graphGenerator(data)
	
		return send_file('fig.png',mimetype='image/png')
		
@app.route('/docrate', methods=['GET', 'POST'])
def rate():
	if request.method == 'GET':
		return render_template('docrate.html')
	elif request.method == 'POST':
		convertor1=request.form.get('converter1')
		convertor2=request.form.get('converter2')
		temp=convertor2
		convertor2=convertor2.strip()
		convertor2=convertor2.split(' ')
		convertor2.append(convertor1)
		x=list()
		y=list()
		prevdate = DT.date.today()
		for i in range(10):
			data=requests.get(url+'/'+str(prevdate),params={'base':convertor1, 'symbols':convertor2})
			prevdate = prevdate - DT.timedelta(days=30)
			data=data.json()
			x.insert(0,data.get('date'))
			y.insert(0,data.get('rates').get(temp))
		plt.figure(figsize=(14,5))
		plt.style.use('dark_background')
		axes = plt.gca()
		if min(y)>=10:
			axes.set_ylim([min(y)-10,max(y)+10]) ## LIMITING Y AXIS VALUES
		else:
			axes.set_ylim([0,max(y)+1]) 
		axes.set_xlim([-1,10]) ## LIMITING X AXIS VALUES
		plt.plot(x,y,color='blue',marker='o', markerfacecolor='white', markersize=5)
		for xy in zip(x, y):                                       
			plt.annotate('%.3f' % xy[1], xy=xy)
		plt.fill_between(x,y, color='blue', alpha='0.3')
		plt.ylabel(temp, color='white')
		plt.xlabel('DATE', color='white')
		plt.title('RATE FLUCTUATION w.r.t 1 '+convertor1, color='white')
		plt.savefig('static/fig.png', dpi=300)
		plt.close()
	return send_file('static/fig.png',mimetype='image/png')

@app.route('/docDate', methods=['GET', 'POST'])
def dateExchange():
	if request.method == 'GET':
		return render_template('docDate.html')
	elif request.method == 'POST':
		base=request.form.get('base')
		base=base.strip()
		date=request.form.get('date')
		data=requests.get(url+'/'+date,params={'base':base})
		graphGenerator(data)
	
		return send_file('fig.png',mimetype='image/png')

if __name__ == '__main__':
	app.run(use_reloader=True, debug=True)
	
