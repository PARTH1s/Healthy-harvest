from django.shortcuts import render
import joblib
import requests
from django.http import HttpResponse
import pandas as pd
from .models import Success
data = pd.read_csv('agriculture.csv')

# Success model is a model having successful crops of a given state
# load data from csv file and store it in database
model = joblib.load('savedModel.sav')
def load(request):
    records = Success.objects.all()
    records.delete()
    tmp_data=pd.read_csv('state_wise_crop_success.csv')
    # create records in database
    records = [
        Success(
            State = tmp_data.iloc[row][1], 
            Crop = tmp_data.iloc[row][2],
            SuccessRate = tmp_data.iloc[row][3],
        )
        for row in range(0, len(tmp_data))
    ]

    Success.objects.bulk_create(records)
    return HttpResponse('<h1> Data loaded successfully </h1>')

# Page where User will enter the values
def index(request):
    return render(request, "main/index.html")

def schemes(request):
    return render(request, "main/schemes.html")

def result(request):
    return render(request, "main/result.html")

def seasons(request):
    # def season(request):
	summer = data[(data['temperature']>30) & (data['humidity']>50)]['label'].unique()
	winter = data[(data['temperature']<29) & (data['humidity']>30)]['label'].unique()
	rainy = data[(data['rainfall']>200) & (data['humidity']>30)]['label'].unique()
	return render(request,"main/seasons.html",{'summer':summer,'winter':winter,'rainy':rainy})
    # return render(request, "main/seasons.html")
def climate(request):
	
	df = data.iloc[0:1,:-1]
	label = data['label'].value_counts().index
	return render(request,'main/climate.html',{'df':df,'label':label})

def selectaverage(request):
	result = []
	if request.method == "POST":
		avg = request.POST.get('avg')
		labels = data['label'].value_counts().index
		for label in labels:
			result.append(data[data['label']==label][avg].mean())
	return render(request,'main/avergae_show.html',{'result':result})

def stats(request):
	
	df = data['label'].value_counts().index
	
	return render(request,'main/stats.html',{'df':df})

def selectlabel(request):
	value = {}
   
	if request.method == "POST":
		label = request.POST.get('label')
		x = data[data['label']==label]
		n_min = x['N'].min()
		p_min = x['P'].min()
		k_min = x['K'].min()
		t_min = x['temperature'].min()
		h_min = x['humidity'].min()
		ph_min = x['ph'].min()
		rain_min = x['rainfall'].min()

		minimum = [n_min,p_min,k_min,t_min,h_min,ph_min,rain_min]

		n_mean = int(x['N'].mean())
		p_mean = int(x['P'].mean())
		k_mean = int(x['K'].mean())
		t_mean = int(x['temperature'].mean())
		h_mean = int(x['humidity'].mean())
		ph_mean = int(x['ph'].mean())
		rain_mean = int(x['rainfall'].mean())

		average = [n_mean,p_mean,k_mean,t_mean,h_mean,ph_mean,rain_mean]

		n_max = x['N'].max()
		p_max = x['P'].max()
		k_max = x['K'].max()
		t_max = x['temperature'].max()
		h_max = x['humidity'].max()
		ph_max = x['ph'].max()
		rain_max = x['rainfall'].max()

		maximum = [n_max,p_max,k_max,t_max,h_max,ph_max,rain_max]
		value['minimum']=minimum
		value['average']=average
		value['maximum']=maximum
        
		
	return render(request,'main/stats_show.html',value)

# Crop prediction and sending result to result.html
def result(request):
    l = []
    l.append(int(request.GET['N']))
    l.append(int(request.GET['P']))
    l.append(int(request.GET['K']))
    l.append(int(request.GET['T']))
    l.append(int(request.GET['Humidity']))
    l.append(int(request.GET['pH']))
    l.append(int(request.GET['Rainfall']))
    state = request.GET['State']

    # predicting the best crop for given conditions
    ans = model.predict([l])

    # get weather details of given state using openweathermap API
    weatherData=requests.get('http://api.openweathermap.org/data/2.5/weather?q='+state+'&appid=72adf46e1fc74893b5312ba1b87fd7c0')
    weatherData=weatherData.json()

    # get top 5 successful crops of given state
    res = Success.objects.filter(State=state).order_by('-SuccessRate')[:5]
    temp = weatherData['main']['temp']
    temp = round(temp-273.15, 2)
    return render(request, "main/result.html", {"ans":ans[0], "res": res, "state": weatherData['name'], "temp": temp, "wind": weatherData["wind"]["speed"], "weatherData": weatherData})

"""
Sample result returned by openweathermap API
{'coord': {'lon': 78.5, 'lat': 23.5}, 
'weather': [{'id': 804, 'main': 'Clouds', 'description': 'overcast clouds', 'icon': '04n'}],
 'base': 'stations',
  'main': {'temp': 287.13, 'feels_like': 285.97, 'temp_min': 287.13, 'temp_max': 287.13, 'pressure': 1016, 'humidity': 53, 'sea_level': 1016, 'grnd_level': 948},
   'visibility': 10000,
    'wind': {'speed': 4.17, 'deg': 85, 'gust': 9.1}, 
    'clouds': {'all': 86}, 'dt': 1640642177, 
    'sys': {'country': 'IN', 'sunrise': 1640654790, 'sunset': 1640693294}, 
    'timezone': 19800, 
    'id': 1264542, 
    'name': 'Madhya Pradesh',
     'cod': 200}
"""

# mandi data
def prices(request):
    pricesData = requests.get('https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070?api-key=579b464db66ec23bdd000001f7324fe93fcb45b046a2600a7adc2cc8&format=json&offset=0&limit=1000')
    pricesData = pricesData.json()
    recs = pricesData['records']
    minPrice = "N/A"
    maxPrice = "N/A"
    state = request.GET['stateOfMandi']
    crop = request.GET['crop']
    data = []
    for record in recs:
        if record["state"] == state and record["commodity"] == crop :
            
            data.append(record["state"],record["crop"],record["min_price"],record["max_price"],record["market"],record["district"])
            minPrice = record["min_price"]
            maxPrice = record["max_price"]
           
    return render(request, "main/index.html", {"state": state, "crop": crop, "minPrice": minPrice, "maxPrice": maxPrice, "data":data})

def temp(request):
    pricesData = requests.get('https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070?api-key=579b464db66ec23bdd000001f7324fe93fcb45b046a2600a7adc2cc8&format=json&offset=0&limit=1000')
    """ 
    pricesData = pricesData.json()
    recs = pricesData['records']
    minPrice = "N/A"
    maxPrice = "N/A"
    state = "Andhra Pradesh"
    crop = "Gur(Jaggery)"
    states = set()
    crop = set()
    for record in recs:
        states.add(record["state"])
        crop.add(record["commodity"]) 
        if record["state"] == state and record["commodity"] == crop :
            minPrice = record["min_price"]
            maxPrice = record["max_price"]
            break  
    """
    

    return HttpResponse(pricesData,content_type="application/json")
    