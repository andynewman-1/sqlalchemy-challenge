from flask import Flask, jsonify

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc
import numpy as np
import pandas as pd
import datetime as dt

# create engine to hawaii.sqlite
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

#Flask Setup
app = Flask(__name__)

# reflect an existing database into a new model
Base = automap_base()

# reflect tables
Base.prepare(autoload_with=engine)

# reflect an existing database into a new model
Base = automap_base()

# reflect tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#Flask Routes


@app.route("/")
def welcome():
    return (
        f"Welcome to the Climate API<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations</br>"
        f"/api/v1.0/tobs</br>"
        f"/api/v1.0/temperature/[StartDate]</br>"
        f"/api/v1.0/temperature/[StartDate]/[EndDate]</br>"
        f"Note: Use yyyy-mm-dd format for dates"
    )

##Precipitation /api/v1.0/precipitation
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Calculate the date one year ago from the latest date in the data set
    latest_date = session.query(func.max(Measurement.date)).scalar()
    date = dt.datetime.strptime(latest_date, "%Y-%m-%d")
    one_year_ago = date - dt.timedelta(days=365)

    # Query the date and precipitation values for the last 12 months
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).all()

    # Close Session
    session.close()

    # Convert the query results to a dictionary with date as the key and prcp as the value
    precipitation_data = {}
    for date, prcp in results:
        precipitation_data[date] = prcp

    # Return the JSON representation of the precipitation data dictionary
    return jsonify(precipitation_data)

##Stations /api/v1.0/stations (Returns jsonified data of all of the stations in the database (3 points))
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all stations
    results = session.query(Measurement.station, Station.name).distinct().all()

    # Close Session
    session.close()

    # Convert the query results to a list of station names
    station_list = []
    for result in results:
            station_dict = {
                "station": result[0],
                "name": result[1]
            }
            station_list.append(station_dict)

    # Return the JSON representation of the station list
    return jsonify(station_list)

##Tobs /api/v1.0/tobs (Returns jsonified data for the most active station (USC00519281) (3 points)
## Only returns the jsonified data for the last year of data (3 points))

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Set the most active station ID
    most_active_station = "USC00519281"

# Retrieve the lowest, highest, and average temperature for the most active station
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.station == most_active_station).\
        first()

    # Extract the results
    lowest_temp = results[0]
    highest_temp = results[1]
    avg_temp = results[2]

    tobs_dict = {"station" : most_active_station,
                 "stats": {
         "lowest temp" : lowest_temp,
         "highest temp" : highest_temp,
         "average temp" : round(avg_temp,2)
         }} 
    return jsonify(tobs_dict)

##/api/v1.0/<start>
@app.route("/api/v1.0/temperature/<start_date>")
def temperature_stats(start_date):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the minimum, maximum, and average temperatures from the given start date to the end of the dataset
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start_date).\
        all()

    
    #latest date for final output
    latest_date = session.query(func.max(Measurement.date)).scalar()
    # Close Session
    session.close()

    # Check if any results are found
    if results:
        # Extract the temperature statistics from the results tuple
        min_temp = results[0][0]
        max_temp = results[0][1]
        avg_temp = results[0][2]

        # Create a dictionary to hold the temperature statistics
        temperature_stats = {
            "start_date": start_date,
            "end_date": latest_date,
            "min_temp": min_temp,
            "max_temp": max_temp,
            "avg_temp": avg_temp
        }

        return jsonify(temperature_stats)
    else:
        return jsonify({"error": "No data found for the provided start date."}), 404

##/api/v1.0/<start>/<end>
@app.route("/api/v1.0/temperature/<start_date>/<end_date>")

def temperature_stats_end(start_date, end_date):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the minimum, maximum, and average temperatures from the given start date to the end of the dataset
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).\
        all()

    # Close Session
    session.close()

    # Check if any results are found
    if results:
        # Extract the temperature statistics from the results tuple
        min_temp = results[0][0]
        max_temp = results[0][1]
        avg_temp = results[0][2]

        # Create a dictionary to hold the temperature statistics
        stats_end = {
            "start_date": start_date,
            "end_date": end_date,
            "min_temp": min_temp,
            "max_temp": max_temp,
            "avg_temp": round(avg_temp,2)
        }

        return jsonify(stats_end)
    else:
        return jsonify({"error": "No data found for the provided start date."}), 404
    
#Make runable from terminal
if __name__ == "__main__":
    app.run(debug=True)