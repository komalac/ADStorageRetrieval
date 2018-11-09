import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

#Home/Welcome page
@app.route("/")
def welcome():
    "List all available api routes."
    return (
        f"Precitation Data:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"<br/>Station Data:<br/>"
        f"/api/v1.0/stations<br/>"
        f"<br/>Temprature Data:<br/>"
        f"/api/v1.0/tobs<br/>"
        f"<br/>Temperature Stats (yyyy-mm-dd):<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )


#################################################

#display Percipitation data
@app.route("/api/v1.0/precipitation")
def cprcp():
    
    # Query all prcp
    results = session.query(Measurement.date, Measurement.prcp).all()
    
    # Convert list of tuples into normal list
    prcp = list(np.ravel(results))
    prcpkv = []

    #loop in through the list, create key/value pair
    for i in range(len(prcp)):
        prcpkv.append({'key': prcp[0], 'value': prcp[1]}) 

    #convert into json format
    return jsonify(prcpkv)

#################################################

#display all station details
@app.route("/api/v1.0/stations")
def cstations():
    
    # Query all stations
    results = session.query(Station).all()

    # Create a dictionary from the row data and append to a list of all_passengers
    all_stations = []
    for stsn in results:
        stsn_dict = {}
        stsn_dict["Station ID"] = stsn.station
        stsn_dict["Name"] = stsn.name
        stsn_dict["Latitude"] = stsn.latitude
        stsn_dict["Longitude"] = stsn.longitude
        stsn_dict["Elevation"] = stsn.elevation
        all_stations.append(stsn_dict)

    return jsonify(all_stations)

#################################################

#display temperature details
@app.route("/api/v1.0/tobs")
def tobs():

    #query last date observed
    maxd = dt.datetime.strptime(session.query(func.max(Measurement.date)).scalar(), '%Y-%m-%d')
    lastYear = maxd - dt.timedelta(days=365)

    # query past one year data (from the last date above)
    sel = [Measurement.date, Measurement.prcp]
    date_prcp = session.query(*sel).\
        filter (Measurement.date<maxd).\
        filter (Measurement.date>lastYear).all()
        
    return jsonify(date_prcp)

#################################################

#display temperature stats starting from the date given
@app.route("/api/v1.0/<start>")
def startd(start):

    #query for temp data from the start date given
    startdt = dt.datetime.strptime(start, '%Y-%m-%d')
    stdt_result = session.query(func.max(Measurement.tobs).label("MaximumTemp"), func.min(Measurement.tobs).label("MinimumTemp"), func.avg(Measurement.tobs).label("AverageTemp")).\
                    filter(Measurement.date >= startdt).all()

    return jsonify(stdt_result)

#################################################

#display temperature stats from the start date, till the end date given
@app.route("/api/v1.0/<start>/<end>")
def startend(start, end):

    #query for temp data for the start & end date given
    startdt = dt.datetime.strptime(start, '%Y-%m-%d')
    enddt = dt.datetime.strptime(end, '%Y-%m-%d')
    stedt_result = session.query(func.max(Measurement.tobs).label("MaximumTemp"), func.min(Measurement.tobs).label("MinimumTemp"), func.avg(Measurement.tobs).label("AverageTemp")).\
                    filter(Measurement.date >= startdt).\
                    filter(Measurement.date <= enddt).all()

    return jsonify(stedt_result)

#################################################

if __name__ == '__main__':
    app.run(debug=True, port=5000)


