# convert DWG Utm-Krrgjsh-Gauss Using ArcGIS - arcpy (applicable only for Albania territory)
Conversions of DWG files between coordinate systems UTM-Gauss-KRRGJSH (Albanian territory only).

Requirements: ArcGIS Desktop 10.5+, Windows 7 or 10.

The script it is tested in arcgis 10.5 and 10.7

Using the script:

1 - Download the toolbox file.

2 - Open it using ArcCatalog or ArcMap

3 - Choose the DWG/DXF file and the input coordinate system of current file. It should be one of those: 

		Pulkovo_1942_GK_Zone_4N

		WGS_1984_UTM_Zone_34N

		ETRS_1989_Albania_2010

4 - Run the tools. It will create at same directory two new files.

# Attention
It may fail in the first run. Just close/open arcmap and run the script again.  (this will happen once in your PC)

This will happen because arcmap dont recognize the new Custom Geographic Transformation at the first run.
