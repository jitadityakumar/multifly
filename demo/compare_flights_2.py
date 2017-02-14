# Read two response files and find the best flight combo
# LOGIC
# Read file 1 , pick up each arr (in) , dep (out)
# Read file 2 , for each record of 1 find the closest arr (in) , dep (out)
# Add difference , set in var
# read next record from file 1, find difference
# if difference is lower , set as optimum , continue
import json

# Read response file1
filename1 = "response/response-LON-GVA-GVA-LON-100.json"
with open(filename1) as infile1:
    response1 = json.load(infile1)

filename2 = "response/response-MAD-GVA-GVA-MAD-100.json"
with open(filename2) as infile2:
    response2 = json.load(infile2)



for tripOption1 in response1["trips"]["tripOption"]
