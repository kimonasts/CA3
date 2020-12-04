from main import get_notifications
from main import get_weather
from main import get_news_england
from main import get_alarms

"""
A test routine is implemented to test functions with return statements
"""

def test_get_alarms():
    assert get_alarms()==[]

def test_get_notifications():
    assert get_notifications()==[]

def test_get_weather():
    assert get_weather()==[{"title": "Weather in Exeter", "content": "Temperature: 5.5\u00b0C, Condition: Clouds, Pressure: 981, Humidity: 87"}]

def test_get_news_england():
    assert get_news_england()==[{"title": "Primark chaos as shoppers wait up to 6 HOURS to get inside then face hour-long queue to pay - The Sun", "content": ""}, {"title": "Injuries reported after large explosion in Bristol industrial area - The Guardian", "content": "Avonmouth incident described by emergency services as serious, with multiple casualties"}, {"title": "Sarah Harding: Girls Aloud star reveals she is writing life story following advanced cancer diagnosis - Sky News", "content": "\"I can't deny that things are tough right now\u00a0but I'm fighting as hard as I possibly can and being as brave as I know how.\""}, {"title": "Survey reveals which clubs are best at dealing with European hangovers... and Klopp has impressed - Daily Mail", "content": "Liverpool have enjoyed much success in recent seasons, but Jurgen Klopp has been furious in regular rants at the sheer number of games his side and others are facing amid a hectic schedule."}, {"title": "Royal POLL: Would you choose republicanism over Prince Charles when Queen dies? - Express", "content": "QUEEN ELIZABETH II's popularity is unlikely to trigger the rise of republicanism in the UK. But would you prefer to live in a republic rather than see the Queen's heir Prince Charles becoming king?"}, {"title": "Ole Gunnar Solskjaer told \"go and get your coat\" after Man Utd defeat by PSG - Mirror Online", "content": "Ole Gunnar Solskjaer was initially named Man United boss on a temporary basis, taking the reins from Jose Mourinho in 2018, before impressing and getting the job permanently"}, {"title": "UK weather: Snow and ice warnings for some parts as winter chill bites - Sky News", "content": "The coldest weather is expected in western Scotland overnight on Thursday, where temperatures could drop to an icy -10C (14F)."}, {"title": "Astronomers unveil most detailed 3D map yet of Milky Way - The Guardian", "content": "Images will enable scientists to measure the acceleration of the solar system and the mass of the galaxy"}]