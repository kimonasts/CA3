from flask import Flask, request, render_template
import os
import json
import pyttsx3
import time, sched
from datetime import datetime
import requests
import logging
from uk_covid19 import Cov19API

#a scheduler object is created

#This scheduler object is used to schedule notifications when an alarm goes off
sched_event=sched.scheduler(time.time, time.sleep)

#This scheduler object is used to delete an alarm from the list after it has been gone off
delete_scheduler=sched.scheduler(time.time,time.sleep)

#This scheduler object is used to update the APIS every 15 minutes
update_apis_scheduler=sched.scheduler(time.time,time.sleep)

#This scheduler object is used to announce updates in the notifications list every time an alarm goes off
tts_scheduler=sched.scheduler(time.time,time.sleep)



#this command is used to open the configuration file
config=open('./JSON Files/config.json')

"""
the config file contains a dictionary in it. With the json.loads(config) method we get that dictionary
and we store it in the config_json variable
"""
config_json=json.load(config)

"""
A Flask application is created which will be used later on to run the html interface
and map python code to it.
"""
app=Flask(__name__)

"""
A file named Alarms.json keeps record of the alarms entered by the user. To access that file
the variable alarms_json_filepath is used. What it does first is to access the key "filepaths" of the 
config_json dictionary. The value of that key is a dictionary that contains key value pairs for 
json files to be used for the project. By accessing the key "alarms" we get the filepath for the Alarms.json
file
"""
alarms_json_filepath=config_json['filepaths']['alarms']


"""
News, Weather and Covid APIs Functions
"""

"""
Weather API
"""


def weather_api():
    """
    The weather_api function retrieves data from the OpenWeatherMap API. A dictionary with keys "title" and "content"
    is used to store local weather data and therefore is added to a list. The list in turn is stored to a json file thanks to
    the store_weather function
    """

    """
    A city_name variable is assigned a string value of a city whose name is stored in the config.json file
    so that it can be changed from there if necessary rather than from the source code.
    """
    city_name = config_json['location']
    api_key = config_json['API Keys']['weather']
    link = "https://api.openweathermap.org/data/2.5/weather?q={}&appid={}".format(city_name, api_key)
    weather_json = requests.get(link).json()
    weather_lst = []
    d = {}
    d['title'] = 'Weather in {}'.format(city_name)

    """
    The OpenWeatherMap API returns the temperature in Kelvin units. The first argument of the .format() converts the 
    temperature in Kelvin to degrees Celsius and rounds it to 2 significant figures. The rest of the content includes data
    for Weather Condition, Pressure and Humidity.
    """
    d['content'] = "Temperature: {}°C, Condition: {}, Pressure: {}, Humidity: {}".format(
        str(round((float(weather_json['main']['temp']) - 273.15), 2)), weather_json['weather'][0]['main'],
        weather_json['main']['pressure'], weather_json['main']['humidity'])

    weather_lst.append(d)

    #this function stores weather data in a json file
    store_weather(weather_lst)

"""
The weather_filepath variable is assigned the value of the Weather_notifications.json filepath
which is stored in the config file.
"""
weather_filepath = config_json['filepaths']['Weather_notifications']


def store_weather(weather_list: list):
    """
    The store_weather function is called inside the weather_api() function, retrieves a list as an argument
    that includes local weather data in a dictionary and stores that list in the Weather_notifications.json
    """
    weather_data = json.dumps(weather_list)
    with open(r'{}'.format(weather_filepath), 'w') as weather_json:
        weather_json.write(weather_data)
        weather_json.close()


def get_weather():
    """
    The get_weather function returns a list of the updated local weather data after reading the
    Weather_notifications.json file
    """
    weather_json = open(r'{}'.format(weather_filepath), 'r')
    weather_data = json.load(weather_json)
    return weather_data


"""
News England API
"""


def news_england_api():
    """
    The news_england_api function retrieves news from England from a news API.
    A dictionary with keys "title" and "content" is used to store the 8 most recent news from England
    and therefore is added to a list. The list in turn is stored to a json file thanks to the store_news_england function.
    """
    count=0
    api_key = config_json['API Keys']['news']
    url='https://newsapi.org/v2/top-headlines?country=gb&apiKey={}'.format(api_key)
    news_england=requests.get(url).json()
    news_england_list=[]
    for article in news_england['articles']:
        count += 1
        if count > 8:
            break
        d={}
        d['title']=article['title']
        d['content']=article['description']
        news_england_list.append(d)

    store_news_england(news_england_list)


"""
The news_england_filepath variable is assigned the value of the news_england.json filepath
which is stored in the config file.
"""
news_england_filepath = config_json['filepaths']['News_England']


def store_news_england(news:list):
    """
    The store_news_england function is called inside the news_england_api function, retrieves a list as an argument
    that includes the 8 most recent news in a dictionary and stores that list in the Weather_notifications.json
    """
    news_england_str=json.dumps(news)
    with open(r'{}'.format(news_england_filepath),'w') as news_england_json:
        news_england_json.write(news_england_str)
        news_england_json.close()



def get_news_england():
    """
    The get_news_england function returns a list of the updated news after reading the
    news_england.json file
    """
    news_england_json=open(r'{}'.format(news_england_filepath),'r')
    news_england=json.load(news_england_json)
    return news_england

"""
Public Health England API
"""

def local_covid_data():
    """
    The local covid data function uses the uk_covid19 module to retrieve local covid infection rates
    for a British city. A Cov19API object gets two parameters, a list of length one that stores a city name and a
    dictionary cases_and_deaths that provides local covid info including the number of new cases and deaths as well as the
    total number of cases and deaths at that city.

    A dictionary with keys 'title' and 'content' is created and adds the value of the difference in new cases between the current and
    the previous day, also calculating the percentage of increase or decrease in the new cases depending on that difference.
    """
    local_only = [
        'areaName={}'.format(config_json['location'])
    ]
    cases_and_deaths = {
        "date": "date",
        "areaName": "areaName",
        "areaCode": "areaCode",
        "newCasesByPublishDate": "newCasesByPublishDate",
        "cumCasesByPublishDate": "cumCasesByPublishDate",
        "newDeathsByDeathDate": "newDeathsByDeathDate",
        "cumDeathsByDeathDate": "cumDeathsByDeathDate"
    }
    """
    A Cov19API object is created. The local_only list is stored in the filters parameter of the Cov19API object
    whereas the dictionary cases_and_deaths formats the structure parameter.
    """
    api = Cov19API(filters=local_only, structure=cases_and_deaths)
    #a json object is assigned to the data variable
    data = api.get_json()

    cases_current_and_previous_day=[]

    #We get the cases of the current and the previous date
    for i in range(2):
        cases_current_and_previous_day.append(data['data'][i]['newCasesByPublishDate'])

    #difference in cases between the current and the previous date is calculated
    diff_in_cases=cases_current_and_previous_day[0]-cases_current_and_previous_day[1]
    cases_increased=False
    cases_decreased=False

    #the if statements determine whether cases have been increased decreased or remained stable
    if diff_in_cases>0:
        cases_increased=True
        percentage_of_increase=(diff_in_cases/cases_current_and_previous_day[1])*100
    elif diff_in_cases<0:
        cases_decreased=True
        percentage_of_decrease=(diff_in_cases/cases_current_and_previous_day[1])*100

    covid_data=[]
    d={}
    d['title'] = "Latest Covid data for {}. Date: {}".format(data['data'][0]['areaName'], data['data'][0]['date'])
    if cases_increased:
         d['content']="New cases: {} , New covid cases in {} were increased by {} from yesterday, Percentage of increase of the new cases in {}: {}%"\
             .format(data['data'][0]['newCasesByPublishDate'],data['data'][0]['areaName'],diff_in_cases,data['data'][0]['areaName'],percentage_of_increase)
    elif cases_decreased:
        d['content'] = "New cases: {}, New covid cases in {} were decreased by {} from yesterday, Percentage of decrease of the new cases in {}: {}%" \
                .format(data['data'][0]['newCasesByPublishDate'],data['data'][0]['areaName'], str(diff_in_cases)[1:],data['data'][0]['areaName'] ,percentage_of_decrease)
    else:
        d['content'] = "New cases: {}, New covid cases in {} are the same as yesterday's ones".format(data['data'][0]['newCasesByPublishDate'],data['data'][0]['areaName'])

    covid_data.append(d)

    store_covid_data(covid_data)

#the covid_filepath variable stores the filepath of the COVID19_notifications.json file
covid_filepath=config_json['filepaths']['COVID19_notifications']

def store_covid_data(covid_lst:list):
    """
    The store_covid_england function is called inside the local_covid_data function, retrieves a list as an argument
    that includes the latest local covid data and stores it into a json file named COVID19_notifications
    """
    covid_data_str=json.dumps(covid_lst)
    with open(r'{}'.format(covid_filepath),'w') as covid_json:
        covid_json.write(covid_data_str)
        covid_json.close()

def get_covid_data():
    """
        The get_covid_data function returns a list of the updated local covid data after reading the
        COVID19_notifications.json file
    """
    covid_json = open(r'{}'.format(covid_filepath), 'r')
    covid_data_list = json.load(covid_json)
    return covid_data_list

#the API_state_json_filepath variable stores the filepath of the API_state.json file
API_state_json_filepath=config_json['filepaths']['API_state']

#the update_frequency variable stores the frequency to which API call are conducted in seconds
update_frequency=config_json['update_frequency']
def update_apis():
    """
    The update apis function is called at the routed to the '/index' page controller function and is used to conduct
    API calls at a specific frequency. The frequency value is stored in the config file so that the developer doesn't
    need to access the source code to change it and is calculated in seconds.

    The function interacts with a json file called API_state.json. At first it is checked whether the file is empty.
    If so, the should_update boolean variable is set from False to True and then, the current datetime is entered to the json file and more
    specifically to a dictionary as the value of the 'last_datetime' key. After then a try except is used to check whether there is internet
    connection so that the API calls are conducted. If not a ConnectionError is raised and the function prevents the program from
    conducting the API calls.

    If the file is not empty, the API_state.json file is read and the value of the 'last_datetime' key is stored to a variable called
    last_datetime. The function then saves the current datetime in the current_dtm variable and calculates the difference in seconds
    between the current and the latest datetime. If that difference is greater or equal than the update frequency value in the config file,
    a request for an API call is made given that there is Internet Connection.

    With the try except statement used the function has the ability to test external services and more specifically whether
    data can be retrieved from those services or not depending on the Internet Connection.
    """
    should_update=False
    d={}
    if os.stat(API_state_json_filepath).st_size == 0:
        should_update=True
    else:
        read_API_state_json=open(API_state_json_filepath,'r')
        last_datetime=datetime.strptime(json.load(read_API_state_json)['last_datetime'],'%Y-%m-%d %H:%M:%S')
        current_time = time.strftime("%H:%M:%S")
        current_datetime = str(datetime.now().date()) + " " + current_time
        current_dtm = datetime.strptime(current_datetime, '%Y-%m-%d %H:%M:%S')

        diff=current_dtm-last_datetime
        diff_seconds = diff.total_seconds()

        if diff_seconds>=update_frequency:
            should_update = True

    if should_update:
        d['last_datetime'] = str(datetime.now().date()) + ' ' + time.strftime("%H:%M:%S")
        with open(API_state_json_filepath, 'w') as API_state_write:
            API_state_write.write(json.dumps(d))
            API_state_write.close()
        try:
            weather_api()
            news_england_api()
            local_covid_data()
        except:
            raise ConnectionError


def tts_request(announcement:str):
    """
    The function tts_request gets a string argument named announcement
    and converts it into oral speech.
    """
    engine = pyttsx3.init()
    engine.say(announcement)
    engine.runAndWait()


def text_to_speech_alarm_announcement(alarm_time:str):
    """
    The function text_to_speech_alarm_announcement gets a string argument alarm_time where the alarm entered
    by the user is stored. The function runs after an alarm is scheduled and informs the user
    about the date and time of the alarm.
    """

    """
    The months dictionary is used to substitute the numeric value of a month in the
    alarm with the actual month itself.
    """
    months_dict = {1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June",
                   7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"}
    """
    The days dictionary is used to substitute the numeric value of a day in the alarm with its corresponding
    ordinal number. 
    """
    days = {1: "1st", 2: "2nd", 3: "3rd", 4: "4th", 5: "5th", 6: "6th", 7: "7th", 8: "8th", 9: "9th", 10: "10th"
        , 11: "11th", 12: "12th", 13: "13th", 14: "14th", 15: "15th", 16: "16th", 17: "17th", 18: "18th", 19: "19th",
            20: "20th"
        , 21: "21st", 22: "22nd", 23: "23rd", 24: "24th", 25: "25th", 26: "26th", 27: "27th", 28: "28th",
            29: "29th", 30: "30th", 31: "31st"}

    """
    The hours_d dictionary is used to substitute the hours returned after an alarm was scheduled with the
    numbers we use to represent those hours in the oral speech. E.g. When the hour is 13:06 in the oral speech
    we say it's one oh six. 
    """
    hours_d = {13: 1, 14: 2, 15: 3, 16: 4, 17: 5, 18: 6, 19: 7,
               20: 8, 21: 9, 22: 10, 23: 11, 0: 12}

    """
    After an alarm is scheduled, the alarm_time variable is assigned a value of the following format
    yyyy-mm-ddTHH:MM. The alarm_time_l variable is a list of length two, whose first element represents the date
    an alarm was set and its second element represents the respective time the alarm was scheduled for that date.
    """
    alarm_time_l = alarm_time.split('T')

    #we get the value of the year of the alarm
    year = alarm_time_l[0].split('-')[0]
    # we get the value of the month of the alarm
    month = months_dict[int(alarm_time_l[0].split('-')[1])]
    # we get the value of the day of the alarm
    day = days[int(alarm_time_l[0].split('-')[2])]

    #we get the hour the alarm was scheduled
    hours = int(alarm_time.split('T')[1].split(':')[0])
    #we get the value of minute(s) the alarm was scheduled
    mins = alarm_time.split('T')[1].split(':')[1]


    #s = ''
    """
    This if statement checks whether the alarm was entered 
    after the midnight and before the midday of the same day. If so the variable s
    which was initialised as an empty string is now assigned the value of 'AM'. Otherwise,
    the value 'PM' is assigned to the variable s
    """
    if hours >= 0 and hours < 12:
        s = 'AM'
    else:
        s = 'PM'

        """
        This if statement checks whether the alarm hours are 0 or greater than 12. If so, the alarm hours are substituted 
        by the numbers we use to represent them in the oral speech.
        """
    if hours == 0 or hours > 12:
        hours = hours_d[hours]

    #concatenates all the above data (i.e. day, month, year, hours, mins and the variable s)
    announcement = 'Alarm scheduled for the {} of {} {} at {}:{} {}'.format(day, month, year, str(hours), mins, s)

    #The tts function is called to make the announcement
    tts_request(announcement)


def set_alarm(alarm_time:str, alarm_title:str, weather:str, news:str):
    """
    The function set_alarm has 4 arguments:
        1.alarm_time argument which is a string of type YYYY-mm-ddThh:mm returned after the user enters an alarm
        2.alarm_title argument which is the alarm_title entered by the user
        3.weather argument whose value either is the name itself in case the checkbox "Include weather briefing"
        is selected by the user, or None if the opposite happens
        4.news argument whose value either is the name itself in case the checkbox "Include news briefing"
        is selected by the user, or None if the opposite happens

    The set_alarm function generates a list of length one whose element is a dictionary with keys 'title' and 'content'.
    The value of the 'title' key is the title entered by the user at the html interface. As for the 'content' key, its value
    includes the date and time that the alarm was set, as well as the type of notifications to be displayed on the screen
    when the relevant time is reached based on the checkboxes the user selected.
    """
    alarms = []
    alarm_dict = {}

    """
    lines 434-439:
    The commands at those lines are used to convert the YYYY-mm-dd format of the date returned by the program to a 
    dd-mm-YYYY format
    """
    alarm_time_l = alarm_time.split('T')
    date_time = alarm_time_l[0].split('-')
    date_time[0],date_time[2]=date_time[2],date_time[0]
    s='-'
    datetime_dd_mm_yy=s.join(date_time)
    alarm_time_l[0]=datetime_dd_mm_yy

    #the title key of the alarm_dict dictionary is assigned the value of the title input by the user
    alarm_dict['title']=alarm_title

    """
    The if statements below determine the alarm's content
    """
    if not weather and not news:
        alarm_dict['content'] = "{} {} : Covid briefing".format(alarm_time_l[0], alarm_time_l[1])
    elif weather and news:
        alarm_dict['content'] = "{} {} : Weather, covid and news briefing".format(alarm_time_l[0],alarm_time_l[1])
    elif weather and not news:
        alarm_dict['content'] = "{} {} : Weather and covid briefing".format(alarm_time_l[0],alarm_time_l[1])
    elif news and not weather:
        alarm_dict['content'] = "{} {} : News and covid briefing".format(alarm_time_l[0],alarm_time_l[1])

    alarms.append(alarm_dict)
    if not alarms[0]['title']==None:
        store_alarm(alarms)
        text_to_speech_alarm_announcement(request.args.get('alarm'))



def store_alarm(alarms:list):
    """
    This function gets as an argument the alarm that the user entered and
    stores it to a json file called Alarms.json.
    """
    #this if statement checks whether the Alarms.json file is empty
    if os.stat(alarms_json_filepath).st_size == 0:
        #the alarms list is converted to a string so that it can be inserted to the Alarms.json file
        alarms_s=json.dumps(alarms)
        with open(alarms_json_filepath,'w') as f:
            #the alarm is stored in the file
            f.write(alarms_s)
            f.close()
    else:
        """
        At that point we know that the Alarms.json file is not empty. It either contains other alarms or an empty list.
        """

        #Here we read the Alarms.json file
        alarm_file=open(alarms_json_filepath,'r')

        """
        The content of the Alarms.json file is stored at the alarms_json variable as a list using the load function of
        the json module
        """
        alarms_json=json.load(alarm_file)

        #this variable stores the dictionary including the title and the content of the alarm entered by the user
        alarm_to_be_set=alarms[0]

        #this if statement checks whether an alarm is duplicate
        if alarm_is_duplicate(alarm_to_be_set)[0]:
            #the previous alarm is overwritten by the new one
            sched_event.cancel(event=sched_event.queue[alarm_is_duplicate(alarm_to_be_set)[1]])
            delete_scheduler.cancel(event=delete_scheduler.queue[alarm_is_duplicate(alarm_to_be_set)[1]])

            alarms_json[alarm_is_duplicate(alarm_to_be_set)[1]]=alarm_to_be_set
            # the alarms list is converted to a string so that it can be inserted to the Alarms.json file
            alarms_s=json.dumps(alarms_json)
            with open(alarms_json_filepath, 'w') as f:
                # the alarm is stored in the file
                f.write(alarms_s)
                f.close()
        else:
            """
            The alarm entered by the user is not overwritten
            """

            #the alarms_json variable adds the dictionary including the title and the content of the alarm entered by the user
            alarms_json.append(alarm_to_be_set)

            """
            A lambda function is used to store the alarms by date and time. Upcoming alarms are placed 
            at the top of the page. 
            
            Note: The indexes of the date and time in every alarm's content are constant. Therefore we use string slicing
            to get the date and time values and then we convert them to a datetime object.
            """
            sorted_alarms = sorted(alarms_json, key=lambda x: datetime.strptime(x['content'][0:16], '%d-%m-%Y %H:%M'))
            alarms_s = json.dumps(sorted_alarms)
            with open(alarms_json_filepath, 'w') as f:
                f.write(alarms_s)
                f.close()


def alarm_is_duplicate(alarm_to_be_set:dict)->(bool,int):
    """
    This function checks whether an alarm has been set for the same day at the same time.
    It gets the alarm to be set by the user as an argument and returns a tuple. At the index zero,
    a boolean value is returned depending on whether the alarm already exists or not. If the alarm already
    exists True is returned at the index zero.

    If the user enters an alarm which has the same date and time with an already existing one in the Alarms.json,
    the function returns the index of the alarm that already exists in the file at the index one of the tuple. Otherwise,
    it returns None.
    """
    alarm_exists = False
    alarm_file = open(alarms_json_filepath, 'r')
    alarms_json = json.load(alarm_file)
    index=None
    """
    This for loop iterates through the alarms_json list and checks
    whether the alarm entered by the user has the same date and time with
    another that already exists in the Alarms.json file.
    """
    for alarm in alarms_json:
        if alarm_to_be_set['content'][0:16]==alarm['content'][0:16]:
            alarm_exists = True
            index=alarms_json.index(alarm)
            break

    return alarm_exists, index


def cancel_alarm(alarm_to_be_deleted:str):
    """
    The cancel alarm function is used to dismiss an alarm
    when the user presses the x button. The condition to delete an
    alarm is that the Alarms.json is not empty. Is this holds, a for loop runs
    and checks if the alarm['title'] is the same as the alarm_to_be_deleted value. If so, the index of the dictionary element
    with the same title as the alarm_to_be_deleted value is found and then that dictionary element is removed from the list.
    """
    if not os.stat(alarms_json_filepath).st_size == 0:
        alarm_file = open(alarms_json_filepath, 'r')
        alarms_json = json.load(alarm_file)
        for alarm in alarms_json:
            if alarm['title']==alarm_to_be_deleted:
                index=alarms_json.index(alarm)
                alarms_json.pop(index)
                if len(sched_event.queue)!=0 and len(delete_scheduler.queue)!=0:
                    """
                    Every time an alarm is cancelled, their respective events are cancelled from their
                    schedulers gueues as well
                    """
                    sched_event.cancel(event=sched_event.queue[index])
                    delete_scheduler.cancel(event=delete_scheduler.queue[index])
                    tts_scheduler.cancel(event=tts_scheduler.queue[index])
                break
        alarms_s = json.dumps(alarms_json)
        with open(alarms_json_filepath, 'w') as f:
            f.write(alarms_s)
            f.close()


def get_alarms()->list:
    """
    This function is used to update alarms to the html interface
    """
    if os.stat(alarms_json_filepath).st_size == 0:
        return
    else:
        a=open(alarms_json_filepath, 'r')
        alarms_lst=json.load(a)
        return alarms_lst


def schedule_event(alarm_time:str,weather:str,news:str):
    """
    The schedule event function takes 3 arguments:
        1.alarm_time argument which is a string of type YYYY-mm-ddThh:mm returned after the user enters an alarm
        2.weather argument whose value either is the name itself in case the checkbox "Include weather briefing"
        is selected by the user, or None if the opposite happens
        3.news argument whose value either is the name itself in case the checkbox "Include news briefing"
        is selected by the user, or None if the opposite happens

    This function is used to trigger an alarm...
    """

    """
    lines 612-625 are used to calculate the difference in seconds between the alarm's date and time
    and the current date and time.
    """
    d = datetime.now().date()
    current_time = time.strftime("%H:%M:%S")
    current_datetime = str(d) + " " + current_time
    current_dtm = datetime.strptime(current_datetime, '%Y-%m-%d %H:%M:%S')

    alarm_time_l=alarm_time.split('T')
    j=' '
    alarm_datetime=j.join(alarm_time_l)

    alarm_dtm = datetime.strptime(alarm_datetime, '%Y-%m-%d %H:%M')
    diff = alarm_dtm - current_dtm
    #print(alarm_time)
    #print(current_time)
    delay = diff.total_seconds()
    print("Delay is " + str(delay))

    """
    The if statements below determine the events to be scheduled
    """

    if not weather and not news:
        #Only Covid Data will be displayed at the notifications list after the alarm goes off
        sched_event.enter(int(delay), 1, add_notifications, [get_covid_data(), ])
        #The alarm will be deleted automatically from the Alarms.json file after triggered
        delete_scheduler.enter(int(delay), 1, delete_alarm_automatically)
        #The program will reassure that the alarm has been triggered with a text-to-speech request
        tts_scheduler.enter(int(delay), 1, trigger_alarm_announcement)
    elif weather and news:
        #Covid, weather and top news stories will be displayed at the notifications list after the alarm goes off
        sched_event.enter(int(delay), 1, add_notifications, [get_covid_data(), get_weather(), get_news_england()])
        # The alarm will be deleted automatically from the Alarms.json file after triggered
        delete_scheduler.enter(int(delay), 1, delete_alarm_automatically)
        # The program will reassure that the alarm has been triggered with a text-to-speech request
        tts_scheduler.enter(int(delay), 1, trigger_alarm_announcement)
    elif weather and not news:
        #Covid and weather will be displayed at the notifications list after the alarm goes off
        sched_event.enter(int(delay), 1, add_notifications, [get_covid_data(), get_weather()])
        # The alarm will be deleted automatically from the Alarms.json file after triggered
        delete_scheduler.enter(int(delay), 1, delete_alarm_automatically)
        # The program will reassure that the alarm has been triggered with a text-to-speech request
        tts_scheduler.enter(int(delay), 1, trigger_alarm_announcement)
    elif news and not weather:
        # Covid and top news storied will be displayed at the notifications list after the alarm goes off
        sched_event.enter(int(delay), 1, add_notifications, [get_covid_data(), get_news_england()])
        # The alarm will be deleted automatically from the Alarms.json file after triggered
        delete_scheduler.enter(int(delay), 1, delete_alarm_automatically)
        # The program will reassure that the alarm has been triggered with a text-to-speech request
        tts_scheduler.enter(int(delay), 1, trigger_alarm_announcement)

#this variable stores the filepath of the Merged_notifications.json
merged_notifications_filepath = config_json['filepaths']['Merged_notifications']

def add_notifications(*args):
    """
    The add_notifications function takes a list of arguments and is called inside a scheduler object at the
    schedule event function. A merged list is used to combine data retrieved from the APIs and add them to do the
    Merged_notification.json file when an alarm goes off.
    """
    merged_list = []
    if os.stat(merged_notifications_filepath).st_size == 0:
        """
        Merged_notifications.json is empty
        """
        merged_notifs_file=open(merged_notifications_filepath,'w')
        for arg in args:
            #every argument is added to the merged_list
            merged_list+=arg

        # the merged list is converted to a string so that it can be inserted to the Merged_notifications.json file
        notifs_s = json.dumps(merged_list)
        merged_notifs_file.write(notifs_s)
        merged_notifs_file.close()
    else:
        """
        Merged_notifications.json is not empty
        """
        merged_notifs_file_r = open(merged_notifications_filepath, 'r')
        notifs_json=json.load(merged_notifs_file_r)
        notifs_json.clear()
        for arg in args:
            # every argument is added to the merged_list
            merged_list=merged_list+arg
        notifs_json=merged_list
        notifs_s=json.dumps(notifs_json)
        merged_notifs_file_w = open(merged_notifications_filepath, 'w')
        merged_notifs_file_w.write(notifs_s)
        merged_notifs_file_w.close()

def trigger_alarm_announcement():
    """
    This function instructs the program to make a text to speech announcement every time an alarm is triggered
    """
    announcement='The time is {} and the first alarm in the list has been triggered'.format(get_time_for_speech())
    tts_request(announcement)

def get_time_for_speech()->str:
    """
    This function returns the time in a form so that it can be announced appropriately (e.g. when hours are 13 and minutes are 0
    in the oral speech we say that it's is one o'clock. So the number 13 should be replaced by the number one and this is achieved
    thanks to the hours_d dictionary and the last if statement of the function)
    """
    current_time=time.strftime("%H:%M")
    hours_d = {13: 1, 14: 2, 15: 3, 16: 4, 17: 5, 18: 6, 19: 7,
               20: 8, 21: 9, 22: 10, 23: 11, 0: 12}
    """
    This if statement checks whether the alarm was entered 
    after the midnight and before the midday of the same day. If so the variable s
    which was initialised as an empty string is now assigned the value of 'AM'. Otherwise,
    the value 'PM' is assigned to the variable s
    """
    hours=int(current_time[0:2])
    mins=current_time[3:]

    if hours >= 0 and hours < 12:
        s = 'AM'
    else:
        s = 'PM'

        """
        This if statement checks whether the alarm hours are 0 or greater than 12. If so, the alarm hours are substituted 
        by the numbers we use to represent them in the oral speech.
        """
    if hours == 0 or hours > 12:
        hours = hours_d[hours]

    t=str(hours)+':'+mins+" "+s

    return t

    #tts_request(announcement)


def delete_alarm_automatically():
    """
    This function deletes an alarm automatically after it has gone off.
    """
    if os.stat(alarms_json_filepath).st_size != 0:
        a = open(alarms_json_filepath, 'r')
        alarms_lst = json.load(a)
        """
        alarms_lst.pop(0) is used since the alarm which is deleted automatically is always 
        the alarm at the index zero of the alarm list
        """
        alarms_lst.pop(0)
        alarms_s = json.dumps(alarms_lst)

        #The Alarms.json file is updated.
        with open(alarms_json_filepath, 'w') as f:
            f.write(alarms_s)
            f.close()


def dismiss_notification(notif_to_be_deleted:str):
    """
    This function is used to delete notifications from the Merged_Notifications list
    """
    merged_notifications_filepath = config_json['filepaths']['Merged_notifications']
    if not os.stat(merged_notifications_filepath).st_size == 0:
        notif_file = open(merged_notifications_filepath, 'r')
        notifs_json = json.load(notif_file)
        for notif in notifs_json:
            if notif['title']==notif_to_be_deleted:
                notifs_json.pop(notifs_json.index(notif))
                break
        notifs_s = json.dumps(notifs_json)
        with open(merged_notifications_filepath, 'w') as f:
            f.write(notifs_s)
            f.close()


def get_notifications()->list:
    """
    This function is used to update notifications to the html interface
    """
    merged_notifications_filepath=config_json['filepaths']['Merged_notifications']
    if os.stat(merged_notifications_filepath).st_size == 0:
        return []
    else:
        a=open(merged_notifications_filepath, 'r')
        notifs_lst=json.load(a)
        return notifs_lst


@app.route('/')
def main_page():
    """
    Every time the main page is opened notifications and alarms are removed from their respective json files
    """
    with open(alarms_json_filepath,'w') as alarms_json:
        alarms_json.write('[]')
        alarms_json.close()

    with open(merged_notifications_filepath,'w') as notifs_json:
        notifs_json.write('[]')
        notifs_json.close()

    return render_template('CA3.html',alarms=get_alarms(),title='Daily Briefing',notifications=get_notifications(),image=config_json['filepaths']['page_image'])

#this variable is used to store the filepath of the logfile
logfile_path=config_json['filepaths']['logfile']

@app.route('/index')
def controller():
    sched_event.run(blocking=False)
    delete_scheduler.run(blocking=False)
    tts_scheduler.run(blocking=False)

    #A log file is used to log all the events that happen
    logging.basicConfig(filename=logfile_path)

    update_apis()

    alarm_time=request.args.get('alarm')
    alarm_item=request.args.get("alarm_item")
    alarm_title=request.args.get('two')
    weather=request.args.get('weather')
    news=request.args.get('news')
    notif=request.args.get('notif')

    #if the user schedules an alarm
    if alarm_time:
        d = datetime.now().date()
        current_time = time.strftime("%H:%M")
        dtm = str(d) + " " + current_time

        alarm_datetime_yyyy_mm_dd_hh_mm=alarm_time.split('T')[0]+" "+alarm_time.split('T')[1]
        #current_datetime is a datetime object
        current_datetime = datetime.strptime(dtm, '%Y-%m-%d %H:%M')
        #alarm_datetime is a datetime object
        alarm_datetime = datetime.strptime(alarm_datetime_yyyy_mm_dd_hh_mm, '%Y-%m-%d %H:%M')

        #the if statement checks whether the alarm_datetime os equal than the current_datetime
        if alarm_datetime<current_datetime or alarm_datetime==current_datetime:
            tts_request("You can't set an alarm for that date and time")
        else:
            set_alarm(alarm_time, alarm_title, weather, news)
            schedule_event(alarm_time,weather,news)

    # If the x button of an alarm textbox is pressed, that textbox is dismissed from the Alarms.json file
    if alarm_item:
        cancel_alarm(alarm_item)

    #If the x button of a notification textbox is pressed, that textbox is dismissed from the Merged_notifications.json file
    if notif:
        dismiss_notification(notif)

    return render_template('CA3.html', alarms=get_alarms(), title='Daily Briefing',notifications=get_notifications(),image=config_json['filepaths']['page_image'])





if __name__=="__main__":
    app.run()
