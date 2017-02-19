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
import requests

def display_time(timestamp):

	# this regex removes all colons and all 
	# dashes EXCEPT for the dash indicating + or - utc offset for the timezone
	conformed_timestamp = re.sub(r"[:]|([-](?!((\d{2}[:]\d{2})|(\d{4}))$))", '', timestamp)
	
	# split on the offset to remove it. use a capture group to keep the delimiter
	split_timestamp = re.split(r"([+|-])",conformed_timestamp)
	main_timestamp = split_timestamp[0]
	sign = split_timestamp[1]
	offset = split_timestamp[2]
	output_datetime = datetime.datetime.strptime(main_timestamp, "%Y%m%dT%H%M")
	output_datetime = str(output_datetime)+" "+str(sign)+str(offset)
	return output_datetime

def find_time_diff(out1,in1,out2,in2):
	fmt="%Y-%m-%d %H:%M:%S"

	out1=datetime.datetime.strptime(out1,fmt)
	out2=datetime.datetime.strptime(out2,fmt)

	in1=datetime.datetime.strptime(in1,fmt)
	in2=datetime.datetime.strptime(in2,fmt)

	if (out1 > out2):
		out_diff = out1 - out2
	else:
		out_diff = out2 - out1

	if (in1 > in2):
		in_diff = in1 - in2
	else:
		in_diff = in2 - in1

	total_diff = out_diff + in_diff
	return total_diff


def convert_to_eur(ccy,amount):

	if (ccy=="EUR"):
		return float(amount)

	with open("ccy.json") as outfile:
		ccy_json = json.load(outfile)

	factor = ccy_json["rates"][ccy]

	convert = float(amount) / float(factor)
	convert = round(convert,2)
	return float(convert)


def str_to_datetime(timestamp):
	fmt="%Y-%m-%d %H:%M:%S"
	obj=datetime.datetime.strptime(str(timestamp),fmt)
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

def print_trip_details(trip,c):
	print("==========Trip "+str(c)+" "+trip[c,"saleTotal"]+"==========")

	for i in range(1,trip[c,'numSlices']+1):
		print("---------- Slice "+str(i)+" Duration:"+trip[c,i,"sliceDuration"]+"----------")
		for j in range(1,trip[c,i,'numSegments']+1):
			for k in range(1,trip[c,i,j,"numLegs"]+1):
				print(trip[c,i,j,"flight"]+" "+trip[c,i,j,"bookingCode"]+" "+trip[c,i,j,k,"origin"]+"-"+trip[c,i,j,k,"destination"]+" "+trip[c,i,j,k,"aircraft"]+" "+trip[c,i,j,k,"legDuration"]+" "+trip[c,i,j,k,"mileage"])
				print("Dep "+trip[c,i,j,k,"depTimeDisp"]+" Arr "+trip[c,i,j,k,"arrTimeDisp"])
			if (trip[c,i,j,"connectionDuration"]!=""):
				print("Connection time "+trip[c,i,j,"connectionDuration"])

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
					details[counter,sliceCounter,segmentCounter,legCounter,"arrTimeDisp"]=display_time(arrTime)
					details[counter,sliceCounter,segmentCounter,legCounter,"depTimeDisp"]=display_time(depTime)
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
							if (str_to_datetime(maxInDepTime) > str_to_datetime(depTimeGMT)):
								maxInDepTime=depTimeGMT
						details[counter,"MaxInDepTime"]=str(maxInDepTime)

				if 'connectionDuration' not in segment:
					details[counter,sliceCounter,segmentCounter,"connectionDuration"]=""
				else:
					connectionDuration=segment["connectionDuration"]
					hours=connectionDuration/60
					mins =connectionDuration%60
					details[counter,sliceCounter,segmentCounter,"connectionDuration"]=str(hours)+"h "+str(mins)+"m"
	return details

query=dict()

# Read response file1
query[0,"filename"] = "response/response-LON-SFO-SFO-LON-100.json"
query[1,"filename"] = "response/response-MAD-SFO-SFO-MAD-100.json"

for i in range(0,2):
	with open(query[i,"filename"]) as infile:
		query[i,"response"] = json.load(infile)
	query[i,"trip"]=file_to_dict(query[i,"response"])

trip1=query[0,"trip"]
trip2=query[1,"trip"]

best=dict()
out1=trip1[1,'MaxOutArrTime']
in1 =trip1[1,"MaxInDepTime"]
out2=trip2[1,"MaxOutArrTime"]
in2 =trip2[1,"MaxInDepTime"]
best[0,"diff"]=find_time_diff(out1,in1,out2,in2)
best[0,"price"]=abs(convert_to_eur(trip1[1,"currency"],trip1[1,"value"]) - convert_to_eur(trip2[1,"currency"],trip2[1,"value"]))
best[0,"trip1"]=1
best[0,"trip2"]=1
best_diff=best[0,"diff"]
best_price=best[0,"price"]
best_1=1
best_2=1


for i in range (1,int(trip1['counter'])+1):

	out1=trip1[i,"MaxOutArrTime"]
	in1= trip1[i,"MaxInDepTime"]
	out2=trip2[1,"MaxOutArrTime"]
	in2= trip2[1,"MaxInDepTime"]
	best[i-1,"diff"]=find_time_diff(out1,in1,out2,in2)
	best[i-1,"price"]=abs(convert_to_eur(trip1[i,"currency"],trip1[i,"value"]) - convert_to_eur(trip2[1,"currency"],trip2[1,"value"]))
	best[i-1,"trip1"]=i
	best[i-1,"trip2"]=1

	# for each trip in trip1, find the best flight in trip2
	for j in range (1,int(trip2['counter'])+1):

		out1=trip1[i,"MaxOutArrTime"]
		in1= trip1[i,"MaxInDepTime"]
		out2=trip2[j,"MaxOutArrTime"]
		in2= trip2[j,"MaxInDepTime"]

		diff = find_time_diff(out1,in1,out2,in2)
		if (diff < best[i-1,"diff"]):
			best[i-1,"diff"]=diff
			best[i-1,"trip1"]=i
			best[i-1,"trip2"]=j

		price1=convert_to_eur(trip1[i,"currency"],trip1[i,"value"])
		price2=convert_to_eur(trip2[j,"currency"],trip2[j,"value"])
		price_diff=abs(price1-price2)
		if (price_diff < best[i-1,"price"]):
			best[i-1,"price"]=price_diff

	if (best[i-1,"diff"] < best_diff):
		best_diff=best[i-1,"diff"]
		best_1=best[i-1,"trip1"]
		best_2=best[i-1,"trip2"]

	if (best[i-1,"price"] < best_price):
		best_price = best[i-1,"price"]

print("All time best diff "+str(best_diff)+" "+str(best_1)+"-"+str(best_2))
print("All time best price diff - EUR "+str(best_price))

price1 = convert_to_eur(trip1[best_1,"currency"],trip1[best_1,"value"])
price2 = convert_to_eur(trip2[best_2,"currency"],trip2[best_2,"value"])
current_price_diff = abs(price1 - price2)
print("Current price diff EUR "+str(current_price_diff))

print_trip_details(trip1,best_1)
print_trip_details(trip2,best_2)
