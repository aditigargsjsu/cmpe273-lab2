import logging
#logging.basicConfig(level=logging.DEBUG)
from spyne import Application, rpc, ServiceBase, \
    Integer, Unicode
from spyne import Iterable
from spyne.protocol.http import HttpRpc
from spyne.protocol.json import JsonDocument
from spyne.server.wsgi import WsgiApplication
import json
import urllib2
import time
import datetime
from flask import Flask, abort
from flask import request
from model import db
from model import User
from model import CreateDB
from model import app as application
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text
import os
import sqlalchemy

DATABASE = 'crime_database'
PASSWORD = 'Password'
USER = 'root'
HOSTNAME = 'localhost'

class CrimeService(ServiceBase):
    @rpc(float, float, float, _returns=Unicode)
    def checkcrime(ctx, lat, lon, radius):
#        database = CreateDB(hostname = 'localhost')
        engine = sqlalchemy.create_engine('mysql://%s:%s@%s'%(USER, PASSWORD, HOSTNAME))
        engine.execute("DROP DATABASE IF EXISTS %s "%(DATABASE))
        engine.execute("CREATE DATABASE IF NOT EXISTS %s "%(DATABASE))
        db.create_all()
        
        # Get Raw data from api.spotcrime. Store it in JSON format in cjdata
        cjdata = json.load(urllib2.urlopen('https://api.spotcrime.com/crimes.json?lat=%s&lon=%s&radius=%s&key=.'%(lat,lon,radius)))
        cjcrimes = cjdata['crimes']
        print 'cjcrimes is',cjcrimes
        no_of_crimes=len(cjcrimes)
        for i in range (0,no_of_crimes):  
            crime_type = cjcrimes[i]['type']
            crime_address = str(cjcrimes[i]['address'])
            crime_street = crime_address
            
            if 'BLOCK' in crime_address:
                if 'BLOCK BLOCK' in crime_address:
                    temp = crime_address.split('BLOCK BLOCK ')
                    crime_street = str(temp[1])
                elif 'BLOCK OF' in crime_address:
                    temp = crime_address.split('BLOCK OF ')
                    crime_street = str(temp[1])
                elif 'BLOCK' in crime_address:
                    temp = crime_address.split('BLOCK ')
                    crime_street = str(temp[1])
            else:
                crime_street = crime_address
            
            crime_timestamp = cjcrimes[i]['date']
            struct_time = time.strptime(crime_timestamp, "%m/%d/%y %I:%M %p")
            if struct_time.tm_hour==1 or struct_time.tm_hour==2:
                crime_time = '12:01am-3am'
            if struct_time.tm_hour==3:
                if struct_time.tm_min==0:
                    crime_time = '12:01am-3am'
                else:
                    crime_time = '3:01am-6am'
                    
            if struct_time.tm_hour==4 or struct_time.tm_hour==5:
                crime_time = '3:01am-6am'
            if struct_time.tm_hour==6:
                if struct_time.tm_min==0:
                    crime_time = '3:01am-6am'
                else:
                    crime_time = '6:01am-9am'

            if struct_time.tm_hour==7 or struct_time.tm_hour==8:
                crime_time = '6:01am-9am'
            if struct_time.tm_hour==9:
                if struct_time.tm_min==0:
                    crime_time = '6:01am-9am'
                else:
                    crime_time = '9:01am-12noon'

            if struct_time.tm_hour==10 or struct_time.tm_hour==11:
                crime_time = '9:01am-12noon'
            if struct_time.tm_hour==12:
                if struct_time.tm_min==0:
                    crime_time = '9:01am-12noon'
                else:
                    crime_time = '12:01pm-3pm'

            if struct_time.tm_hour==13 or struct_time.tm_hour==14:
                crime_time = '12:01pm-3pm'
            if struct_time.tm_hour==15:
                if struct_time.tm_min==0:
                    crime_time = '12:01pm-3pm'
                else:
                    crime_time = '3:01pm-6pm'

            if struct_time.tm_hour==16 or struct_time.tm_hour==17:
                crime_time = '3:01pm-6pm'
            if struct_time.tm_hour==18:
                if struct_time.tm_min==0:
                    crime_time = '3:01pm-6pm'
                else:
                    crime_time = '6:01pm-9pm'

            if struct_time.tm_hour==19 or struct_time.tm_hour==20:
                crime_time = '6:01pm-9pm'
            if struct_time.tm_hour==21:
                if struct_time.tm_min==0:
                    crime_time = '6:01pm-9pm'
                else:
                    crime_time = '9:01pm-12midnight'

            if struct_time.tm_hour==22 or struct_time.tm_hour==23:
                crime_time = '9:01pm-12midnight'
            if struct_time.tm_hour==0:
                if struct_time.tm_min==0:
                    crime_time = '9:01pm-12midnight'
                else:
                    crime_time = '12:01am-3am'

            # Have entries to put in the database.
            # Need to put crime_type, crime_street and crime_time.

            # Should add a try, except
            user = User(crime_street, crime_type, crime_time)
            db.session.add(user)
        #for loop should end here
        db.session.commit()
        engine.execute('use %s;'%(DATABASE))
        
        # Top three streets with most crime
        results_streets = engine.execute('select street, count(*) as crime from user group by street order by crime DESC limit 3;')
        top_three_streets=[]
        for row in results_streets:
            top_three_streets.append(row.street)

        # Collecting numbers of crime types and time of crimes
        assault = engine.execute("select count(type) as count from user where type='Assault';")
        for row in assault:
            assault_count = row.count

        arrest = engine.execute("select count(type) as count from user where type='Arrest';")
        for row in arrest:
            arrest_count = row.count

        burglary = engine.execute("select count(type) as count from user where type='Burglary';")
        for row in burglary:
            burglary_count = row.count

        robbery = engine.execute("select count(type) as count from user where type='Robbery';")
        for row in robbery:
            robbery_count = row.count

        theft = engine.execute("select count(type) as count from user where type='Theft';")
        for row in theft:
            theft_count = row.count

        other = engine.execute("select count(type) as count from user where type='Other';")
        for row in other:
            other_count = row.count

        time_12am_3am = engine.execute("select count(type) as count from user where time='12:01am-3am';")
        for row in time_12am_3am:
            time_12am_3am_count = row.count

        time_3am_6am = engine.execute("select count(type) as count from user where time='3:01am-6am';")
        for row in time_3am_6am:
            time_3am_6am_count = row.count

        time_6am_9am = engine.execute("select count(type) as count from user where time='6:01am-9am';")
        for row in time_6am_9am:
            time_6am_9am_count = row.count

        time_9am_12pm = engine.execute("select count(type) as count from user where time='9:01am-12noon';")
        for row in time_9am_12pm:
            time_9am_12pm_count = row.count

        time_12pm_3pm = engine.execute("select count(type) as count from user where time='12:01pm-3pm';")
        for row in time_12pm_3pm:
            time_12pm_3pm_count = row.count

        time_3pm_6pm = engine.execute("select count(type) as count from user where time='3:01pm-6pm';")
        for row in time_3pm_6pm:
            time_3pm_6pm_count = row.count

        time_6pm_9pm = engine.execute("select count(type) as count from user where time='6:01pm-9pm';")
        for row in time_6pm_9pm:
            time_6pm_9pm_count = row.count

        time_9pm_12am = engine.execute("select count(type) as count from user where time='9:01pm-12midnight';")
        for row in time_9pm_12am:
            time_9pm_12am_count = row.count

        result_output = json.dumps({'total crime':no_of_crimes, 'the_most_dangerous_streets': top_three_streets, 'crime_type_count':{'Assault':assault_count, 'Arrest':arrest_count, 'Burglary':burglary_count, 'Robbery':robbery_count, 'Theft':theft_count, 'Other':other_count},'event_time_count':{'12:01am-3am':time_12am_3am_count,'3:01am-6am':time_3am_6am_count,'6:01am-9am':time_6am_9am_count,'9:01am-12noon':time_9am_12pm_count,'12:01pm-3pm':time_12pm_3pm_count,'3:01pm-6pm':time_3pm_6pm_count,'6:01pm-9pm':time_6pm_9pm_count,'9:01pm-12midnight':time_9pm_12am_count}})
        yield result_output
        

application = Application([CrimeService],
    tns='spyne.crime',
    in_protocol=HttpRpc(validator='soft'),
    out_protocol=JsonDocument()
)

if __name__ == '__main__':
    from wsgiref.simple_server import make_server

    wsgi_app = WsgiApplication(application)
    server = make_server('0.0.0.0', 8000, wsgi_app)
    server.serve_forever()
























##class HelloWorldService(ServiceBase):
##    @rpc(Unicode, Integer, _returns=Iterable(Unicode))
##    def say_hello(ctx, name, times):
##        for i in range(times):
##            yield 'Hello, %s' % name

##application = Application([HelloWorldService],
##    tns='spyne.examples.hello',
##    in_protocol=HttpRpc(validator='soft'),
##    out_protocol=JsonDocument()
##)
