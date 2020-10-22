#osu-scorescraper

import json
import requests
import csv
import random
import sys
import time
import pandas as pd
from time import sleep

#api key here
api_key = 'API_KEY'

def main():
	#get total maps wanted & file name from user
	data = user_input()
	count = int(data[0])
	file_name = data[1]
	
	url = 'https://osu.ppy.sh/api/get_scores?k='+api_key+'&limit=1&b='

	#results contains maps.csv 
	#master is the final spreadsheet to be returned
	results, master = [],[]
	with open("maps.csv") as csvfile:
	    reader = csv.reader(csvfile) 
	    for row in reader: 
	        results.append(row)

	percent = int(len(results)/100)
	check_ids = permute(len(results)-1)

	checks = 1
	start = time.time()
	for index in check_ids:
		#line below changes condition for map to be checked 
		if float(results[index][2])>2.75 and float(results[index][2])<3.5:
			resp = requests.get(url+results[index][0]) 
			temp = json.loads(resp.content)

			for each in temp:
				perfect = int(each['count300'])
				great = int(each['count100'])
				good = int(each['count50'])
				miss = int(each['countmiss'])

				hitobjects = perfect+great+good+miss
				mods = each['enabled_mods']
				
				username = each['username']
				#weird edge-case
				if username[0] == '-': 
					username = username[1:]


				accuracy = float((perfect + great/3 + good/6))/float(hitobjects)

				#line below controls conditions for mods and acc 
				if mods in ['72','1030','104','1062','16456','17414']:
					print(username + ' | ' + results[index][1] +  ' | ' + results[index][0])
					master.append({'player': username, 
								   'song': results[index][1], 
								   'accuracy': round((accuracy*100),2), 
								   'sr':round(float(results[index][2]),2),
								   'bpm':round(float(results[index][3]),2),
								   'length':round(float(results[index][4]),2),
								   'link': 'https://osu.ppy.sh/b/' + str(results[index][0])})

		#percentage and time display
		if checks % percent == 0 and count == 0:
			end = time.time()
			print("\n-----------------------------------------------------------------------")
			print("Map checks are "+ str(int(checks/percent)) + "%" + " complete.")
			print("Time elapsed: "+str(int((end-start)/60))+"m "+str(round(end-start,2)%60)+"s.")
			print("Estimated time left: "+str(int(((end-start)/(checks/percent)*(100-checks/percent))/60))+" minutes")
			print("-----------------------------------------------------------------------\n")

		checks = checks + 1
		if len(master) == count and count: break

	pd.DataFrame(master).to_csv(file_name + '.csv')

def rebuild():
	fetch_url = 'https://osu.ppy.sh/api/get_beatmaps?k='+api_key+'&m=0&since='
	date = '2006-01-01'
	container = {}

	for i in range(1,500):
	    resp = requests.get(fetch_url+date)
	    temp = json.loads(resp.content)
	    for each in temp:
	        if each['approved'] in ['1','2','4']:
	        	container[each['beatmap_id']] = {'song': each['artist']+' - '+each['title'] +' ['+each['version']+']', 
	            								 'sr':each['difficultyrating'],
	            								 'bpm':each['bpm'],
	            								 'combo':each['max_combo'],
	            								 'length':each['total_length'],
	            								 'ar':each['diff_approach'],
	            								 'od':each['diff_overall'],
	            								 'cs':each['diff_size']}

	    if len(temp) == 500: 
	    	date = temp[499]['approved_date']
	    else: 
	    	break
	    sleep(1.0)

	map_df = pd.DataFrame.from_dict(container, orient='index')
	map_df.to_csv('maps.csv', index=True)

def user_input():
	print("\n-----------------------------------------------------------------------\n")
	dec = input("Would you like to rebuild the map database? (y/n):   ")
	if dec is 'y': 
		rebuild()
	elif dec is 'n': 
		print("")
	else:
		print("\nAborting program.\n")
		sys.exit()

	count = input("How many maps do you want? (input 0 for all):   ")
	file_name = input("Enter the desired name of output file:   ")
	print("\nStarting map search...\n")

	return [count, file_name]

#permute and get_next serve to scramble the map order
#so that requesting n maps will give a random n every time
def get_next(v) :   
	n = len(v) 
	index = random.randint(0, n - 1) 
	num = v[index]  

	v[index], v[n - 1] = v[n - 1], v[index] 
	v.pop()  

	return num 
  
def permute(n):
	arr = []
	v = [0]*n 

	for i in range(n): 
		v[i] = i + 1
	while len(v): 
		arr.append(get_next(v)) 

	return arr 

main()



# MOD IDS:
# N/A = 0
# NF = 1
# EZ = 2
# HD = 8
# HR = 16
# SD = 32
# DT = 64
# HT = 256
# NC = 512
# FL = 1024
# SO = 4096
# PF = 16384

# FREQUENT COMBINATIONS
# HDHR = 24 / HDHRSD = 56
# HDDT = 72 / HDDTSD = 104 / HDNC = 584 / HDNCSD = 616
# HDDTHR = 88 / HDDTHRSD = 120 / HDNCHR = 600 / HDNCHRSD = 632

