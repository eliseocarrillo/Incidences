#-------------------------------------------------------------------------------
# Name:        3. Tracks incidences
# Purpose:     This script allows user to introduce information about an
#              incidence in a track, registering it in a point feature class.
#              After that, an email is sent to the person in charge with all
#              the information.
#
# Author:      Eliseo Carrillo
#
# Created:     13/02/2016
# Copyright:   (c) Eliseo 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import arcpy
import os
import datetime
import time
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders

start_time = time.time()

# Workspace
wksp = "Database Connections\EDITOR@EDICION@PROYECTO.sde"
arcpy.env.workspace = wksp
arcpy.env.overwriteOutput = True

# Input arguments
    # Incidence
tipoIncidencia = arcpy.GetParameterAsText(0)

detalleIncidencia = arcpy.GetParameterAsText(1)

if tipoIncidencia == "Otro":
    tipoIncidencia = detalleIncidencia

    # User location
userLocation = arcpy.GetParameter(2)

# Incidences feature class
incidencias = r'Database Connections\EDITOR@EDICION@PROYECTO.sde\PROYECTO.DBO.RedViaria\PROYECTO.DBO.Incidencias'

# Tracks feature class
tracks = r'Database Connections\SO@DEFAULT@PROYECTO.sde\PROYECTO.DBO.RedViaria\PROYECTO.DBO.Caminos'

# Tracks feature class into feature layer
tracksLyr = "capaCaminos"
arcpy.MakeFeatureLayer_management(tracks, tracksLyr)

# Track selection by user location
in_layer = tracksLyr
select_features = userLocation
search_distance = 50 #50 metros de distancia de busqueda (teniendo en cuenta
                     #la precision de un gps normal)
overlap_type = "WITHIN_A_DISTANCE"
arcpy.SelectLayerByLocation_management(in_layer, overlap_type, select_features, search_distance)

# Feature layer from previous track selection
arcpy.MakeFeatureLayer_management("capaCaminos", "capaCaminosSelecc")

edit = arcpy.da.Editor(wksp)
edit.startEditing(False, True)
edit.startOperation()

# Track name
with arcpy.da.SearchCursor("capaCaminosSelecc", ["NAME", "OBJECTID"]) as cursor:
    for row in cursor:
        nameCamino = row[0]
        oidCamino = row[1]

# xy coordinates user location
with arcpy.da.SearchCursor(userLocation, ["SHAPE@XY"]) as cursor:
    for row in cursor:
        xyCamino = row[0]

# Insert cursor to introduce all the information in a new feature into the
# incidences feature class
fields = ["NAME", "Incidencia", "Fecha", "SHAPE@XY"]
cursor = arcpy.da.InsertCursor(incidencias, fields)
for x in range(0,1):
    cursor.insertRow((nameCamino, tipoIncidencia, datetime.datetime.now(), xyCamino))

del cursor

edit.stopOperation()
edit.stopEditing(True)

# Incidence report
line1 = "Incidencia:"
line2 = "\n\t Camino: {0}".format(nameCamino)
line3 = "\n\t Coordenadas UTM: {0}".format(xyCamino)
line4 = "\n\t Fecha de registro: {0}".format(datetime.datetime.now())
line5 = "\n\t Tipo: {0}".format(tipoIncidencia)
message = line1 + line2 + line3 + line4 + line5

# Email with incident report
    # This will log you into your gmail account--this is where the mail will be sent from.
gmail_user = "pncazorla.agente@gmail.com" # String e.g. mypassword
gmail_pwd = "s0brin0ik0" # String e.g. Password

    # The parameters
to = "pncazorla.tecnico@gmail.com" # String  e.g. recipient@gmail.com
subject = "Incidencia en el camino {0}".format(nameCamino) # String e.g. "This is a test"
text = message # String e.g. "Subject test"

def mail(to, subject, text):
    msg = MIMEMultipart()

    msg['From'] = gmail_user
    msg['To'] = to
    msg['Subject'] = subject

    msg.attach(MIMEText(text))
    mailServer = smtplib.SMTP("smtp.gmail.com", 587)
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login(gmail_user, gmail_pwd)
    mailServer.sendmail(gmail_user, to, msg.as_string())
    mailServer.close()

    # Now send the email. This line calls the function above.
mail(to, subject, text)

# Out message
messageOut = "La incidencia se ha registrado correctamente"
arcpy.SetParameter(4, messageOut)

print("--- %s seconds ---" % (time.time() - start_time))