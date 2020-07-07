from __future__ import print_function
import  time, os, threading
import sys
from flask import Flask, render_template, request, json, redirect,url_for
from flaskext.mysql import MySQL
from getSNMP import ComandSNMP,TupleComandSNMP
import pygal


app = Flask(__name__)
getDataThread = threading.Thread()
stop_threads = False

mysql = MySQL()
#mysql login
app.config['MYSQL_DATABASE_USER'] = 'flask'
app.config['MYSQL_DATABASE_PASSWORD'] = '**Hol4Mund0**'
app.config['MYSQL_DATABASE_DB'] = 'snmp'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()

inputValues = list()
outputValues = list()

@app.route('/')
def main():
	cursor.execute("SELECT * FROM agents;")
	data = cursor.fetchall()
	return render_template('index.html',data=data)

@app.after_request
def add_headers(response):
	response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
	response.headers['Cache-Control'] = 'public,max-age=0'
	return response;

@app.route('/addAgent')
def addAgent():
	return render_template('addAgent.html')

@app.route('/createAgent',methods=['GET','POST'])
def signUp():
	host  = request.form['host']
	community = request.form['community']
	version = request.form['version']
	port = request.form['port']
	os = ComandSNMP(community,host,"1.3.6.1.2.1.1.1.0")
	interfaces = TupleComandSNMP(community,host,"1.3.6.1.2.1.2.1.0")
	reboot = TupleComandSNMP(community,host,"1.3.6.1.2.1.1.3.0")
	cursor.execute("INSERT INTO agents VALUES(%s,%s,%s,%s,%s,%s,%s)",(host,community,version,port,os,reboot,interfaces))
	conn.commit()
	return redirect(url_for('main'))

@app.route('/delete',methods=['GET','POST'])
def delete():
	host = request.form['host']
	print(host, file=sys.stderr)
	cursor.execute("DELETE FROM agents WHERE host='"+host+"'")
	conn.commit()
	return redirect(url_for('main'))

@app.route('/returned',methods=['GET','POST'])
def returned():
	return redirect(url_for('main'))

@app.route('/report',methods=['GET','POST'])
def report():
	host = request.form['host']
	#get the community from the DB using the host
	cursor.execute("SELECT comunity FROM agents WHERE host='"+host+"'")
	community = cursor.fetchone()
	community = community[0]
	#RAM STATUS
	bytesTotales = TupleComandSNMP(community,host,"1.3.6.1.4.1.2021.4.5.0")
	bytesUsados = TupleComandSNMP(community,host,"1.3.6.1.4.1.2021.4.6.0")
	bytesCompartidos = TupleComandSNMP(community,host,"1.3.6.1.4.1.2021.4.13.0")
	bytesBuffer = TupleComandSNMP(community,host,"1.3.6.1.4.1.2021.4.14.0")
	usada = float(bytesUsados)/float(bytesTotales)*100
	compartida = float(bytesCompartidos)/float(bytesTotales)*100
	buffered = float(bytesBuffer)/float(bytesTotales)*100
	libres = 100 - usada - compartida - buffered
	print(str(usada)+"  "+str(compartida)+"  "+str(buffered)+"  "+str(libres))
	ramChart = pygal.Pie()
	ramChart.add('RAM usada',usada)
	ramChart.add('RAM compartida',compartida)
	ramChart.add('RAM en buffer',buffered)
	ramChart.add('RAM libre',libres)
	ramChartData = ramChart.render_data_uri()
	#INPUT TRAFFIC
	inputChart = pygal.Line()
	inputChart.add('Input traffic',inputValues)
	inputChartData = inputChart.render_data_uri()
	#CPU TIMES
	userCPUTime = int(TupleComandSNMP(community,host,'1.3.6.1.4.1.2021.11.9.0'))
	systemCPUTime = int(TupleComandSNMP(community,host,'1.3.6.1.4.1.2021.11.10.0'))
	idleCPUTime = int(TupleComandSNMP(community,host,'1.3.6.1.4.1.2021.11.11.0'))
	niceCPUTime = 100 - userCPUTime - systemCPUTime - idleCPUTime
	cpuChart = pygal.Pie()
	cpuChart.add('User CPU time',userCPUTime)
	cpuChart.add('System CPU Time',systemCPUTime)
	cpuChart.add('Idle CPU Time',idleCPUTime)
	cpuChart.add('No data',niceCPUTime)
	cpuChartData = cpuChart.render_data_uri()
	#OUTPUT TRAFFIC
	outputChart = pygal.Line()
	outputChart.add('Output traffic',outputValues)
	outputChartData = outputChart.render_data_uri()
	return render_template('report.html',ramChartData=ramChartData,inputChartData=inputChartData,cpuChartData=cpuChartData,outputChartData=outputChartData)

@app.route('/activate',methods=['GET','POST'])
def activate():
	host = request.form['host']
	global stop_threads
	stop_threads = False
	#get the community from the DB using the host
	cursor.execute("SELECT comunity FROM agents WHERE host='"+host+"'")
	community = cursor.fetchone()
	community = community[0]
	global getDataThread
	getDataThread = threading.Thread(name='leer',target=leer,args=(host,community,))
	print("activar: "+getDataThread.getName())
	getDataThread.start()
	return redirect(url_for('main'))

@app.route('/desactivate',methods=['GET','POST'])
def desactivate():
	global getDataThread
	print("Desactivar: "+getDataThread.getName())
	global stop_threads
	stop_threads = True
	return redirect(url_for('main'))

def leer(host,community):
	print("Hilo iniciado")
	while True:
		#inputdata graph
		inputTrafic = int(TupleComandSNMP(community,host,"1.3.6.1.2.1.2.2.1.10.3"))
		print("inputTrafic: "+str(inputTrafic))
		inputValues.append(inputTrafic)
		#outputdata graph
		outputTrafic = int(TupleComandSNMP(community,host,"1.3.6.1.2.1.2.2.1.16.3"))
		print("outputTrafic: "+str(outputTrafic))
		outputValues.append(outputTrafic)
		time.sleep(1)
		global stop_threads
		print(stop_threads)
		if stop_threads:
			break
		

if __name__ == '__main__':
	app.run()

