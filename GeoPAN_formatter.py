#!/usr/bin/env python
import string
import math as m
import re

####################################################################
#   This takes points in cartesian coordinates, calculates the     #
#           horizontal distances and uncertainties, and            #
#                formats that for use with GeoPAN.                 #
#                                                                  #
#       List cartesian coordinates in a file in the format:        #
#           point_identifier x_meters y_meters z_meters            #
#                                                                  #
#      List the to-from arrangement in a file in the format:       #
#            point_identifier_from point_identifier_to             #
#                                                                  #
# Set the input files in the controls inside GeoPAN_formatter.py.  #
#           Also set the precision of the measurements,            #
#                 the number of measurement set.                   #
#      The output file name is determined from Project_name.       #
#                                                                  #
#                             To Run:                              #
#                  $ python3 GeoPAN_formatter.py                   #
#                                                                  #
__author__    =  "Jana Barker"                                     #
__copyright__ =  "Copyright (C) 2020 Jana Barker"                  #
__version__   =  "1.0"                                             #
#####################################################################

#####################################################################
######################### Settable Controls #########################
#####################################################################
"""Coordinates"""
Coords_file_name = "Coords.txt"

"""From-To file"""
FromTo_file_name = "FromTo.txt"

Project_name = "PIP-II"

"""Output file name"""
Output_file_name = Project_name+"_HD_output2GeoPAN.txt"

"""Measurement Precisions"""
Sigma_sd = [0.6,1.0] #[mm,ppm] #Slope Distance Precision 
Sigma_za_mgon = 0.15 #[mgon]   #Zenith Angule Precision in mgons

"""Number of measurement sets"""
Number_of_sets_of_distances = 3
Number_of_sets_of_angles = 3

#####################################################################
#####################################################################

#FUNCTIONS
def horizontal_distance(X1,Y1,X2,Y2):
	"""Function calculates horizontal distance from point 1 to point 2
	   from given X1, Y1, X2, Y2"""
	dX = X2 - X1
	dY = Y2 - Y1
	hd = m.sqrt(pow(dX,2)+pow(dY,2))
	return hd

def slope_distance(X1,Y1,Z1,X2,Y2,Z2):
	"""Function calculates slope distance from point 1 to point 2
	   from given X1, Y1, Z1, X2, Y2, Z2"""
	dX = X2 - X1
	dY = Y2 - Y1
	dZ = Z2 - Z1
	sd = m.sqrt(pow(dX,2)+pow(dY,2)+pow(dZ,2))
	return sd
	
def delta_height(Z1,Z2):
	"""Function calculates height difference between point 1 and 2"""
	dH = Z2 - Z1
	return dH

def zenith_angle(X1,Y1,Z1,X2,Y2,Z2):
	hd = horizontal_distance(X1,Y1,X2,Y2)
	sd = slope_distance(X1,Y1,Z1,X2,Y2,Z2)
	if Z2 > Z1:
	  za = m.asin(hd/sd)
	elif Z2 == Z1:
	  za = m.pi/2
	else:
	  za = m.pi - m.asin(hd/sd)
	return za

def Sigma_horizontal_distance(Sigma_sd,Sigma_za,Num_of_sets_ang,Num_of_sets_dist,X1,Y1,Z1,X2,Y2,Z2):
	"""Calculates the standard deviation of slope distance between points 1(from) and 2(to).
	Function takes into account number of sets of sets of distances.
	- Sigma_sd is Standard Deviation of slope distance in two number list format [mm,ppm]
	- Sigma_za is Standard Deviation of the zenith angle in radians float
	- Num_of_sets_of ang and dist is the number of repetition of angular and distance
	  measurement as each can be set differently."""
	za = zenith_angle(X1,Y1,Z1,X2,Y2,Z2)
	sd = slope_distance(X1,Y1,Z1,X2,Y2,Z2)
	c_sd = (Sigma_sd[0] / m.sqrt(Num_of_sets_dist)) / 1000 #Constant precision of the slope distance with X repetitions and in meters
	v_sd = (Sigma_sd[1] / m.sqrt(Num_of_sets_dist)) / 1000000 #ppm part of the precision of the slope distance with X repetitions and in meters
	Sig_za = Sigma_za/m.sqrt(Num_of_sets_ang)
	Sig_hd = m.sqrt(pow(c_sd + v_sd * sd,2) + pow(m.cos(za),2) \
	 * (pow(sd,2) * pow(Sig_za,2) - pow(c_sd + v_sd * sd,2)))
	return Sig_hd


"""Coordinates"""
Coords_file = open(Coords_file_name,'r')
Coords = {}
"""From > To file"""
FromTo_file = open(FromTo_file_name,'r')
FromTo = []


FromTo_Sigma_hd = []# Will be a list of tuples

#VARIABLES CALCULATED
Sigma_za = m.pi*(Sigma_za_mgon/200000)

#CODE
for line in Coords_file.readlines():
	"""Reads in and parses coordinates file. Ignores point notes at the end.
	It can handle multiple occurences of delimeters but not a combination of them."""
	words = re.split(';+|,+|\t+| +',line.strip())
	Coords[words[0]] = (float(words[1]), float(words[2]), float(words[3]))

Coords_file.close()

for line in FromTo_file.readlines():
	"""Reads in and parses From > To file. Ignores anything after two values in a row.
	It can handle multiple occurences of delimeters but not a combination of them."""
	words = re.split(';+|,+|\t+| +',line.strip())
	FromTo.append([words[0],words[1]])
"""CHANGE IF YOU WANT MEASUREMENTS THERE AND BACK OR NOT:
	FromTo.append([words[1],words[0]])"""
	
FromTo_file.close()

"""CHANGE IF YOU HAVE THE INPUT UNSORTED, OTHERWISE BETTER UNSORTED!!!!"""
#FromTo.sort()

for line in FromTo:
	
	FromCoord = Coords[line[0]]
	ToCoord = Coords[line[1]]
	
	Sigma_hd = Sigma_horizontal_distance(Sigma_sd,Sigma_za,Number_of_sets_of_angles,\
	Number_of_sets_of_distances,\
	FromCoord[0],FromCoord[1],FromCoord[2],\
	ToCoord[0],ToCoord[1],ToCoord[2])

#	hd = horizontal_distance(FromCoord[0],FromCoord[1],ToCoord[0],ToCoord[1])
#	print(hd,Sigma_hd)
	FromTo_Sigma_hd.append((line[0],line[1],Sigma_hd))
# print(FromTo_Sigma_hd)
"""formatting:
----+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
             from     to       note        std. dev.  ppm     observation
II_II_II__AAAAAAAA__AAAAAAAA__AAAAAAAA__ssss.ssssspppp.ppppp12345678.12345
 1  0 0   LBNF-1    LBNF-3                 0.000346  1.94                 LBNF TS Horizontal distance
 7  0 0   TC-1      LBNF-2                 0.00009   0.00000       0.00000                    LBNF Zenith angle
 1  0 0   1025_SR   66589                  0.000591                        LBNF Horizontal distance with 3 repetitions using 0.6mm + 1.0ppm
 1  0 0   1025_SR   66589                  0.00059                        LBNF Horizontal distance with 3 repetitions using 0.6mm + 1.0ppm
"""

out_file = open(Output_file_name,"w+")
for line in FromTo_Sigma_hd:
	out_file.write(f" 1  0 0   {line[0].ljust(8)[:8]}  {line[1].ljust(8)[:8]}{15*' '}{str(line[2]).ljust(7)[:7]}{42*' '}{Project_name}\
 Horizontal distance with {Number_of_sets_of_distances} repetitions using {Sigma_sd[0]}mm + {Sigma_sd[1]}ppm\n")
out_file.close()
