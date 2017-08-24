import json

file_directory = 'test.json'

json_data = open(file_directory).read()

data = json.loads(json_data)

start_year = 2013
end_year = 2017
cur_year = 2013

for year in xrange(start_year,end_year+1):
  for smt in xrange(1,3):
    print('https://six.akademik.itb.ac.id/publik/displayprodikelas.php?&semester='+str(smt)+'&tahun='+str(year)+'&th_kur='+str(cur_year))


link_pattern_accepted = 'https:\/\/six\.akademik\.itb\.ac\.id\/publik\/displaydpk\.php\?p=.*%3D%3D'

extention_rejected = 'csv'

for i in xrange(0,len(data['data'])):
  print(data['data'][i]['field_name'])
  print(data['data'][i]['type'])
  print(data['data'][i]['pattern'])
  if (data['data'][i].has_key('filter')):
    print(data['data'][i]['filter'])

  if ((data['data'][i]['count']) == 'any'):
    data_sec = data['data'][i]['data_secondary']
    for j in xrange(0,len(data_sec)):
      print(data_sec[j]['field_name'])
      print(data_sec[j]['type'])
      print(data_sec[j]['pattern'])
      if (data_sec[j].has_key('filter')):
        print(data_sec[j]['filter'])