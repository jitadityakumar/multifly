# Read two response files and find the best flight combo
# LOGIC
# Read file 1 , pick up each arr (in) , dep (out)
# Read file 2 , for each record of 1 find the closest arr (in) , dep (out)
# Add difference , set in var
# read next record from file 1, find difference
# if difference is lower , set as optimum , continue
import json
import re
import datetime

def str_to_datetime(timestamp):
	fmt="%Y-%m-%d %H:%M:%S"
	obj=datetime.datetime.strptime(timestamp,fmt)
	return obj

def time_to_gmt (timestamp):
    "This function converts the google flights timestamp to GMT"

    # this regex removes all colons and all 
    # dashes EXCEPT for the dash indicating + or - utc offset for the timezone
    conformed_timestamp = re.sub(r"[:]|([-](?!((\d{2}[:]\d{2})|(\d{4}))$))", '', timestamp)

    # split on the offset to remove it. use a capture group to keep the delimiter
    split_timestamp = re.split(r"([+|-])",conformed_timestamp)
    main_timestamp = split_timestamp[0]
    if len(split_timestamp) == 3:
        sign = split_timestamp[1]
        offset = split_timestamp[2]
    else:
        sign = None
        offset = None

    # generate the datetime object without the offset at UTC time
    output_datetime = datetime.datetime.strptime(main_timestamp, "%Y%m%dT%H%M")
    if offset:
        # to convert local time to GMT sign must be reversed
        if str(sign) == "-":
            sign = "+"
        else:
            sign = "-"
        # create timedelta based on offset
        offset_delta = datetime.timedelta(hours=int(sign+offset[:-2]), minutes=int(sign+offset[-2:]))
        # offset datetime with timedelta
        output_datetime = output_datetime + offset_delta

    return output_datetime

def file_to_dict (response):
	"This function takes the json data from a file read and outputs a dict"
	counter=0
	details=dict()

	for tripOption in response["trips"]["tripOption"]:
		counter += 1
		details['counter']=counter
		saleTotal=str(tripOption["saleTotal"])
		details[counter,"saleTotal"] = saleTotal
		details[counter,"currency"]  = saleTotal[:3]
		details[counter,"value"]     = saleTotal[3:]

		sliceCounter=0
		maxOutArrTime=""
		maxInDepTime=""
		for slice in tripOption["slice"]:
			# slice is a one way trip eg LHR-SVO-DEL
			# for a return trip
			# slice2 will be DEL-SVO-LHR
			sliceCounter+=1
			details[counter,'numSlices']=sliceCounter
			duration = slice["duration"]
			hours = duration / 60
			mins  = duration % 60
			details[counter,sliceCounter,"sliceDuration"]=str(hours)+"h "+str(mins)+"m"

			segmentCounter=0
			for segment in slice["segment"]:
				# segment is a one way flight
				# eg LHR-SVO-DEL
				# segment 1 LHR-SVO
				# segment 2 SVO-DEL
				# segment is made up of legs
				segmentCounter+=1
				details[counter,sliceCounter,'numSegments']=segmentCounter
				carrier=segment["flight"]["carrier"]
				number =segment["flight"]["number"]
				flight=carrier+"-"+number
				details[counter,sliceCounter,segmentCounter,'flight']=str(flight)
				details[counter,sliceCounter,segmentCounter,'bookingCode']=str(segment["bookingCode"])

				legCounter=0
				for leg in segment["leg"]:
					# leg is a A to B flight
					# eg LHR to SVO in the slice LHR-SVO-DEL
					# legs dont have to be 1 , eg flight YYZ to EZE
					# leg 1 YYZ-SCL
					# leg 2 SCL-EZE
					# The flight number is the same for both
					legCounter+=1
					details[counter,sliceCounter,segmentCounter,"numLegs"]=legCounter
					details[counter,sliceCounter,segmentCounter,legCounter,"aircraft"]=str(leg["aircraft"])
					details[counter,sliceCounter,segmentCounter,legCounter,"origin"]=str(leg["origin"])
					details[counter,sliceCounter,segmentCounter,legCounter,"destination"]=str(leg["destination"])
					duration=leg["duration"]
					hours=duration/60
					mins =duration%60
					details[counter,sliceCounter,segmentCounter,legCounter,"legDuration"]=str(hours)+"h "+str(mins)+"m"
					details[counter,sliceCounter,segmentCounter,legCounter,"mileage"]=str(leg["mileage"])
					arrTime=leg["arrivalTime"]
					depTime=leg["departureTime"]
					arrTimeGMT=time_to_gmt(arrTime)
					depTimeGMT=time_to_gmt(depTime)
					details[counter,sliceCounter,segmentCounter,legCounter,"arrTime"]=str(arrTime)
					details[counter,sliceCounter,segmentCounter,legCounter,"depTime"]=str(depTime)
					details[counter,sliceCounter,segmentCounter,legCounter,"arrTimeGMT"]=str(arrTimeGMT)
					details[counter,sliceCounter,segmentCounter,legCounter,"depTimeGMT"]=str(depTimeGMT)
					if (sliceCounter==1):
						#This is the outgoing slice
						if (maxOutArrTime==""):
							maxOutArrTime=arrTimeGMT
						else:
							if (str_to_datetime(maxOutArrTime) < str_to_datetime(arrTimeGMT)):
								maxOutArrTime=arrTimeGMT
						details[counter,"MaxOutArrTime"]=str(maxOutArrTime)
					if (sliceCounter==2):
						#This is the incoming slice
						if (maxInDepTime==""):
							maxInDepTime=depTimeGMT
						else:
							if (str_to_datetime(maxInDepTime) < str_to_datetime(depTimeGMT)):
								maxInDepTime=depTimeGMT
						details[counter,"MaxInDepTime"]=str(maxInDepTime)

				if 'ConnectionDuration' not in segment:
					details[counter,sliceCounter,segmentCounter,"connectionDuration"]=""
				else:
					connectionDuration=segment["connectionDuration"]
					hours=connectionDuration/60
					mins =connectionDuration%60
					details[counter,sliceCounter,segmentCounter,"connectionDuration"]=str(hours)+"h "+str(mins)+"m"
	return details

# Read response file1
filename1 = "response/response-LON-GVA-GVA-LON-100.json"
with open(filename1) as infile1:
    response1 = json.load(infile1)

filename2 = "response/response-MAD-GVA-GVA-MAD-100.json"
with open(filename2) as infile2:
    response2 = json.load(infile2)

print("load file into dict")
trip1=file_to_dict(response1)
trip2=file_to_dict(response2)


for c in range (1,int(trip1['counter'])+1):
	# for each trip in trip1, find the best flight in trip2


