# Import Dependencies
from flask import Flask, jsonify
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import sqlalchemy
import statistics as st
import numpy as np
import datetime as dt


#Database Setup
engine=create_engine("sqlite:///hawaii.sqlite",connect_args={'check_same_thread': False})
Base=automap_base()
Base.prepare(engine,reflect=True)

measurement=Base.classes.measurement
station=Base.classes.station

#Flask Setup
app = Flask(__name__)

session=Session(engine)
recent_date=session.query(measurement.date).order_by(measurement.date.desc()).first()
x_date=dt.date(2017, 8, 23) - dt.timedelta(days=365)

#Routes
@app.route("/")
def home():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date (in MM-DD-YYYY format)<br/>"
        f"/api/v1.0/start_date/end_date (in MM-DD-YYYY format)")

@app.route("/api/v1.0/precipitation")
def precipitation():

    prp_data=session.query(measurement.date, measurement.prcp).\
    filter(measurement.date >= x_date).all()
    dt_data={}
    
    for row in prp_data:
        dt_data[row.date]=row.prcp
  
    return jsonify(dt_data)

@app.route("/api/v1.0/stations")
def stations():
    stns=session.query(station.station)
    stn_list=[]
    for stn in stns:
        stn_list.append(stn.station)
    
    return jsonify(stations=stn_list)


@app.route("/api/v1.0/tobs")
def temp():
    print("The most active station is USC00519281")
    last_date_stn=session.query(measurement.date).order_by(measurement.date.desc()).filter(measurement.station=='USC00519281').first()
    
    last_date_dict=last_date_stn._asdict()
    last_date=last_date_dict['date']
    year=int(last_date[0:4])
    month=int(last_date[5:7])
    day=int(last_date[8:10])

    y_date=dt.date(year, month, day) - dt.timedelta(days=365)
    temp_data=session.query(measurement.date, measurement.tobs).filter(measurement.date >= y_date).all()
    temp_list=[]
    for t in temp_data:
        temp_list.append(t.tobs)
    return jsonify(temp=temp_list)


@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def max_min_avg(start=None, end=None):
    if end!=None:
        t_range=session.query(measurement).\
        filter(measurement.date>=start).filter(measurement.date<=end).all()
    else:
        t_range=session.query(measurement).\
        filter(measurement.date>=start).all()        

    t_list=[]
    for t in t_range:
        t_list.append(t.tobs)
    
    t_dict={"TMIN": min(t_list),
    "TAVG": round(st.mean(t_list),2),
    "TMAX": max(t_list)}

    return jsonify(t_dict)


if __name__ == "__main__":
    app.run(debug=True)