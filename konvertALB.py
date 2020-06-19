#this script it is created by Florjan Vladi
#this is tested in windows 7+ and ArcGIS Desktop 10.5 and 10.7
#DWG-file should has just Points, Lines, Polygon, Annontation
#all other CAD objects like Hatch, 3dface,civil 3d objects, block references will not be converted
#for the first run it may not work, you just need to restart the arcmap or arccatalog.

import os
import arcpy
import shutil

def main():
    arcpy.env.overwriteOutput = True
    #parameter 1 workspace+dwg
    path = arcpy.GetParameterAsText(0)
    arcpy.AddMessage(path)
    workingDir, dwgName = os.path.split(path)
    arcpy.env.workspace = workingDir
    os.chdir(workingDir)

    try:
        os.makedirs("tempFolder")
        arcpy.CreateFileGDB_management(workingDir+"/tempFolder","test")
    except OSError as e:
        print ("Issue: %s - %s." % (e.filename, e.strerror))
        arcpy.AddMessage("Issue: %s - %s." % (e.filename, e.strerror))

    #parameter 2, current dwg coordinate system (1-UTM, 2-Gauss, 3-KRRGJSH)
    paremater2 = arcpy.GetParameterAsText(1)
    currentSystem = paremater2.split(";")[0]
    arcpy.AddMessage(currentSystem)
    #coordinates definition
    coord = {"1":"utm","2":"gauss","3":"krrgjsh"}

    #systems
    gauss4N = "PROJCS['Pulkovo_1942_GK_Zone_4N',GEOGCS['GCS_Pulkovo_1942',DATUM['D_Pulkovo_1942',SPHEROID['Krasovsky_1940',6378245.0,298.3]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Gauss_Kruger'],PARAMETER['False_Easting',500000.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',21.0],PARAMETER['Scale_Factor',1.0],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Meter',1.0]]"
    utm34N = "PROJCS['WGS_1984_UTM_Zone_34N',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',500000.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',21.0],PARAMETER['Scale_Factor',0.9996],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Meter',1.0]]"
    krrgjsh34N = "PROJCS['ETRS_1989_Albania_2010',GEOGCS['GCS_ETRS_1989',DATUM['D_ETRS_1989',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',500000.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',20.0],PARAMETER['Scale_Factor',1.0],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Meter',1.0]]"
    
    #function to project from UTM to GAUSS and KRRGJSH
    def transU(utm,gauss,krrgjsh):
        name = coord["1"]+"_2_"+coord["2"]+"_7parameters"
        name2 = coord["1"]+"_2_"+coord["3"]+"_7parameters"
        arcpy.CADToGeodatabase_conversion(path,os.path.join(workingDir,"tempFolder\\test.gdb"),coord["1"],1000,utm)
        arcpy.CreateFeatureDataset_management(os.path.join(workingDir,"tempFolder\\test.gdb"),coord["2"],gauss)
        arcpy.CreateFeatureDataset_management(os.path.join(workingDir,"tempFolder\\test.gdb"),coord["3"],krrgjsh)
        try:
            arcpy.CreateCustomGeoTransformation_management(name, utm, gauss, utm_2_gauss(1))
            arcpy.CreateCustomGeoTransformation_management(name2, utm, krrgjsh, utm_2_krrgjsh(-1))
        except:
            print("Transformimi ekziston")
        arcpy.env.workspace = workingDir+"\\tempFolder\\test.gdb\\"+coord["1"]
        lyr = arcpy.ListFeatureClasses()
        for i in lyr:
            if i not in ["Annotation","MultiPatch","Point","Polygon","Polyline"]:
                continue
            arcpy.Project_management(i,os.path.join(workingDir,"tempFolder\\test.gdb",coord["2"],i+"_"+coord["2"]),gauss,name,utm,"NO_PRESERVE_SHAPE", None, "NO_VERTICAL")
            arcpy.Project_management(i,os.path.join(workingDir,"tempFolder\\test.gdb",coord["3"],i+"_"+coord["3"]),krrgjsh,name2,utm,"NO_PRESERVE_SHAPE", None, "NO_VERTICAL")
        for j in range(2):
            arcpy.env.workspace = workingDir+"\\tempFolder\\test.gdb\\"+coord[str(j+2)]
            lyr = arcpy.ListFeatureClasses()
            CADlayers=""
            for i in lyr:
                CADlayers = CADlayers + arcpy.env.workspace+"\\"+i+";"
            arcpy.ExportCAD_conversion(CADlayers,"DWG_R2013",os.path.join(workingDir,dwgName[:-4]+"_"+coord[str(j+2)]+".dwg"),"Ignore_Filenames_in_Tables", "Overwrite_Existing_Files", "")
        #Finisht UTM -> Gauss -> KRRGJSH

    #function to project from Gauss to UTM and KRRGJSH
    def transG(gauss,utm,krrgjsh):
        name = coord["2"]+"_2_"+coord["1"]+"_7parameters"
        name2 = coord["1"]+"_2_"+coord["3"]+"_7parameters"
        arcpy.CADToGeodatabase_conversion(path,os.path.join(workingDir,"tempFolder\\test.gdb"),coord["2"],1000,gauss)
        arcpy.CreateFeatureDataset_management(os.path.join(workingDir,"tempFolder\\test.gdb"),coord["1"],utm)
        arcpy.CreateFeatureDataset_management(os.path.join(workingDir,"tempFolder\\test.gdb"),coord["3"],krrgjsh)
        try:
            arcpy.CreateCustomGeoTransformation_management(name, gauss, utm, utm_2_gauss(-1))
            arcpy.CreateCustomGeoTransformation_management(name2, utm, krrgjsh, utm_2_krrgjsh(-1))
        except:
            print("Transformimi ekziston")
        arcpy.env.workspace = workingDir+"\\tempFolder\\test.gdb\\"+coord["2"]
        lyr = arcpy.ListFeatureClasses()
        for i in lyr:
            if i not in ["Annotation","MultiPatch","Point","Polygon","Polyline"]:
                continue
            arcpy.Project_management(i,os.path.join(workingDir,"tempFolder\\test.gdb",coord["1"],i+"_"+coord["1"]),utm,name,gauss,"NO_PRESERVE_SHAPE", None, "NO_VERTICAL")
            arcpy.Project_management(os.path.join(workingDir,"tempFolder\\test.gdb",coord["1"],i+"_"+coord["1"]),os.path.join(workingDir,"tempFolder\\test.gdb",coord["3"],i+"_"+coord["3"]),krrgjsh,name2,utm,"NO_PRESERVE_SHAPE", None, "NO_VERTICAL")
        for j in range(3):
            if j==1:
                continue
            arcpy.env.workspace = workingDir+"\\tempFolder\\test.gdb\\"+coord[str(j+1)]
            lyr = arcpy.ListFeatureClasses()
            CADlayers=""
            for i in lyr:
                CADlayers = CADlayers + arcpy.env.workspace+"\\"+i+";"
            arcpy.ExportCAD_conversion(CADlayers,"DWG_R2013",os.path.join(workingDir,dwgName[:-4]+"_"+coord[str(j+1)]+".dwg"),"Ignore_Filenames_in_Tables", "Overwrite_Existing_Files", "")
        #Finisht Gauss -> UTM -> KRRGJSH

    #function to project from KRRGJSH to Gauss to UTM
    def transK(krrgjsh,utm,gauss):
        name = coord["3"]+"_2_"+coord["1"]+"_7parameters"
        name2 = coord["1"]+"_2_"+coord["2"]+"_7parameters"
        arcpy.CADToGeodatabase_conversion(path,os.path.join(workingDir,"tempFolder\\test.gdb"),coord["3"],1000,krrgjsh)
        arcpy.CreateFeatureDataset_management(os.path.join(workingDir,"tempFolder\\test.gdb"),coord["1"],utm)
        arcpy.CreateFeatureDataset_management(os.path.join(workingDir,"tempFolder\\test.gdb"),coord["2"],gauss)
        try:
            arcpy.CreateCustomGeoTransformation_management(name, krrgjsh, utm, utm_2_krrgjsh(1))
            arcpy.CreateCustomGeoTransformation_management(name2, utm, gauss, utm_2_gauss(1))
        except:
            print("Transformimi ekziston")
        arcpy.env.workspace = workingDir+"\\tempFolder\\test.gdb\\"+coord["3"]
        lyr = arcpy.ListFeatureClasses()
        for i in lyr:
            if i not in ["Annotation","MultiPatch","Point","Polygon","Polyline"]:
                continue
            arcpy.Project_management(i,os.path.join(workingDir,"tempFolder\\test.gdb",coord["1"],i+"_"+coord["1"]),utm,name,krrgjsh,"NO_PRESERVE_SHAPE", None, "NO_VERTICAL")
            arcpy.Project_management(os.path.join(workingDir,"tempFolder\\test.gdb",coord["1"],i+"_"+coord["1"]),os.path.join(workingDir,"tempFolder\\test.gdb",coord["2"],i+"_"+coord["2"]),gauss,name2,utm,"NO_PRESERVE_SHAPE", None, "NO_VERTICAL")
        for j in range(2):
            arcpy.env.workspace = workingDir+"\\tempFolder\\test.gdb\\"+coord[str(j+1)]
            lyr = arcpy.ListFeatureClasses()
            CADlayers=""
            for i in lyr:
                CADlayers = CADlayers + arcpy.env.workspace+"\\"+i+";"
            arcpy.ExportCAD_conversion(CADlayers,"DWG_R2013",os.path.join(workingDir,dwgName[:-4]+"_"+coord[str(j+1)]+".dwg"),"Ignore_Filenames_in_Tables", "Overwrite_Existing_Files", "")
        #Finisht KRRGJSH -> UTM -> Gauss 

    if currentSystem == utm34N:
        transU(utm34N,gauss4N,krrgjsh34N)
    elif currentSystem == gauss4N:
        transG(gauss4N,utm34N,krrgjsh34N)
    elif currentSystem ==krrgjsh34N:
        transK(krrgjsh34N,utm34N,gauss4N,)
    else:
        print("You system did not matched with any")



    #remove the working directory
    try:
        shutil.rmtree(os.path.join(workingDir,"tempFolder"))
    except OSError as e:
        print ("Error: %s - %s." % (e.filename, e.strerror))

#parameters of coordinate frames UTM and GAUSS
def utm_2_gauss(a):
    utm_gauss = {"dx":44.183,"dy":0.58,"dz":38.489,"rx":2.3867,"ry":2.7072,"rz":-3.5196,"s":8.2703}
    return "GEOGTRAN[METHOD['Coordinate_Frame'],PARAMETER['X_Axis_Translation',{0}],PARAMETER['Y_Axis_Translation',{1}],PARAMETER['Z_Axis_Translation',{2}],PARAMETER['X_Axis_Rotation',{3}],PARAMETER['Y_Axis_Rotation',{4}],PARAMETER['Z_Axis_Rotation',{5}],PARAMETER['Scale_Difference',{6}]]".format(utm_gauss["dx"]*a,utm_gauss["dy"]*a,utm_gauss["dz"]*a,utm_gauss["rx"]*a,utm_gauss["ry"]*a,utm_gauss["rz"]*a,utm_gauss["s"]*a)
#parameters of coordinate frames UTM and KRRGJSH
def utm_2_krrgjsh(a):
    utm_krrgjsh = {"dx":0.0527,"dy":0.0509,"dz":-0.06636,"rx":-0.001456,"ry":-0.008809,"rz":0.014238,"s":0.000958}
    return "GEOGTRAN[METHOD['Coordinate_Frame'],PARAMETER['X_Axis_Translation',{0}],PARAMETER['Y_Axis_Translation',{1}],PARAMETER['Z_Axis_Translation',{2}],PARAMETER['X_Axis_Rotation',{3}],PARAMETER['Y_Axis_Rotation',{4}],PARAMETER['Z_Axis_Rotation',{5}],PARAMETER['Scale_Difference',{6}]]".format(utm_krrgjsh["dx"]*a,utm_krrgjsh["dy"]*a,utm_krrgjsh["dz"]*a,utm_krrgjsh["rx"]*a,utm_krrgjsh["ry"]*a,utm_krrgjsh["rz"]*a,utm_krrgjsh["s"]*a)
 



if __name__=="__main__":
    main()