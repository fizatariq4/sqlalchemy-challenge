# Import the dependencies.
from flask import Flask, jsonify
import datetime as dt
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")


# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

def date_calc():
    latest_date = session.query(func.max(Measurement.date)).scalar()

    latest_date_datetime = dt.datetime.strptime(latest_date, '%Y-%m-%d')
    
    one_year_ago = latest_date_datetime - dt.timedelta(days=365)
  
    previous_start_date = one_year_ago.strftime('%Y-%m-%d')
    end_date = latest_date

    return previous_start_date, end_date

#################################################
# Flask Setup
#################################################
app = Flask(__name__)




#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    return (
        f"Welcome to the Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    date_range = date_calc() 
    date_start = date_range[0]
    date_end = date_range[1]
    
    results = session.query(Measurement.date, Measurement.station, Measurement.prcp).\
                      filter(Measurement.date <= date_end).\
                      filter(Measurement.date >= date_start).all()
                                      
    data_list = []
    for result in results:
        data_dict = {"Date": result[0], "Station": result[1], "Precip": result[2]}
        data_list.append(data_dict)
        
    return jsonify(data_list)


@app.route("/api/v1.0/stations")
def stations():
    stations_data = session.query(Station.station, Station.name).all()
    
    station_list = []
    for station in stations_data:
        station_dict = {"Station_ID": station[0], "Station_name": station[1]}
        station_list.append(station_dict)

    return jsonify(station_list)


@app.route("/api/v1.0/tobs")
def tobs():
    range = date_calc()
    date_end = range[1]
    date_start = range[0]
    tobs = session.query(Measurement.date,Measurement.tobs).\
                            filter(Measurement.date <= date_end).\
                            filter(Measurement.date >= date_start).all()
    list = []
    for temp in tobs:
        dict = {"Date": temp[0], "tobs": temp[1]}
        list.append(dict)

    return jsonify(list)  


@app.route("/api/v1.0/<start>")
def temperature_range(start):
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)) \
                     .filter(Measurement.date >= start) \
                     .order_by(Measurement.date.desc()) \
                     .all()

    temperature_list = []
    print(f"Analysis of temperature at start date")
    for temps in results:
        temperature_dict = {"TMIN": temps[0], "TAVG": temps[1], "TMAX": temps[2]}
        temperature_list.append(temperature_dict)
    
    return jsonify(temperature_list)


@app.route("/api/v1.0/<start>/<end>")
def temperature_range_with_end(start, end):
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                  filter(Measurement.date >= start, Measurement.date <= end).order_by(Measurement.date.desc()).all()
    
    temperature_dict = {
        "TMIN": results[0][0],
        "TAVG": results[0][1],
        "TMAX": results[0][2]
    }

    return jsonify(temperature_dict)


if __name__ == "__main__":
    app.run(debug=True)




