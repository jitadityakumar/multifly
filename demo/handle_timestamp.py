import re
import datetime

timestamp = "2017-05-12T12:10+02:00"
print("original = "+timestamp)

# this regex removes all colons and all 
# dashes EXCEPT for the dash indicating + or - utc offset for the timezone
conformed_timestamp = re.sub(r"[:]|([-](?!((\d{2}[:]\d{2})|(\d{4}))$))", '', timestamp)

print("conformed_timestamp = "+str(conformed_timestamp))

# split on the offset to remove it. use a capture group to keep the delimiter
split_timestamp = re.split(r"([+|-])",conformed_timestamp)
print("split_timestamp "+str(split_timestamp))
main_timestamp = split_timestamp[0]
if len(split_timestamp) == 3:
    sign = split_timestamp[1]
    offset = split_timestamp[2]
else:
    sign = None
    offset = None

print("sign "+str(sign))
print("offset "+str(offset))

# generate the datetime object without the offset at UTC time
output_datetime = datetime.datetime.strptime(main_timestamp, "%Y%m%dT%H%M")
print("without offset = "+str(output_datetime))
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

print("after offset = "+str(output_datetime))
fmt="%Y-%m-%d %H:%M:%S"
obj=datetime.datetime.strptime(str(output_datetime),fmt)
print("time obj "+str(obj))
