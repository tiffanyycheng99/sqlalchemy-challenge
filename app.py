# Python SQL toolkit and Object Relational Mapper
import os
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

import numpy as np
import pandas as pd
import datetime as dt

# Find the most recent date in the data set from measurement table
from datetime import datetime

# Import Flask
from flask import Flask, jsonify

#################################################
# Database Setup 
#################################################

# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
base = automap_base()
base.prepare(engine, reflect=True)

# Reflect Table and Save references to each table
measurement = base.classes.measurement
station = base.classes.station


# Create an app
app = Flask(__name__)

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )
@app.route("/api/v1.0/precipitation")
def precipitation():
    """List all Precipitation Records from last 12 months"""
    # Create a session
    session = Session(engine)

    recent = session.query(measurement.date,measurement.prcp).all()

    session.close()

    # Create a dictionary from row data and append to a list
    all_prcp = []
    for date, prcp in recent:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        all_prcp.append(prcp_dict)
        
    return jsonify(all_prcp)

@app.route("/api/v1.0/stations")
def stations():
    """List Stations"""
    # Create a session
    session = Session(engine)

    stations = session.query(station.station).all()

    session.close() 

    # Convert list of tuples into normal list
    all_station = list(np.ravel(stations))

    return jsonify(all_station)

@app.route("/api/v1.0/tobs")
def tobs():
     # Create a session
    session = Session(engine)

    # Assign the most recent date in measurement table
    recent = datetime.strptime('2017-08-23',"%Y-%m-%d")

    # Get the date to get reference for one year back from most recent date in measurement table
    one_year_back = recent-dt.timedelta(days=366)

    # Query the Measurement table for the Date and TOBS from the most recent 12 months back and sort
    results = session.query(measurement.date,measurement.tobs).\
    filter(measurement.date > one_year_back).\
    order_by(measurement.date).all()

    # Close session
    session.close()

    # Take results and put into dataframe df
    df = pd.DataFrame(results).set_index('date')
    df = df.sort_index()

    # Create a list out of the df series "TOBS"
    all_tobs = df["tobs"].tolist()

    # Return the jsonify list of tobs
    return jsonify(all_tobs)
    
@app.route("/api/v1.0/<start>")
def startdate(start):
    # display inputted <start> date as datetime object
    start_date = datetime.strptime(start,"%Y-%m-%d")

    # Create a session and get min, max, and avg of tobs in table from start date to most recent date in table
    session = Session(engine)
    
    results = session.query(func.min(measurement.tobs),func.max(measurement.tobs),func.sum(measurement.tobs)/func.count(measurement.tobs)).\
        filter(measurement.date >= start_date).all()
    
    # Close session
    session.close()

    # return list of TOBS stats
    return jsonify(results)


@app.route("/api/v1.0/<start>/<end>")
def rangedate(start,end):
    # Display inputted <start> and <end> dates as datetime object
    start_date = datetime.strptime(start,"%Y-%m-%d")
    end_date = datetime.strptime(end,"%Y-%m-%d")

    # Create a session and query the min, max, and avg tobs from the measurement tables within the inputted range
    session = Session(engine)
    
    results = session.query(func.min(measurement.tobs),func.max(measurement.tobs),func.sum(measurement.tobs)/func.count(measurement.tobs)).\
        filter(measurement.date >= start_date).\
        filter(measurement.date <= end_date).all()
    
    # Close session
    session.close()

    # Return the TOBS stats
    return jsonify(results)


if __name__ == '__main__':
    app.run(debug=True)
