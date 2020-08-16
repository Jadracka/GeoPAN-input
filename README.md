# GeoPAN-input
This takes points in cartesian coordinates, calculates the horizontal distances and uncertainties, and formats that for use with GeoPAN. 

List cartesian coordinates in a file in the format:
point_identifier x_meters y_meters z_meters

List the to-from arrangement in a file in the format: 
point_identifier_from point_identifier_to

Set the input files in the controls inside GeoPAN_formatter.py. Also set the precision of the measurements, the number of measurement set. The output file name is determined from Project_name. 

#To Run:
$ python3 GeoPAN_formatter.py
