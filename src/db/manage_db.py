# academic_db.py

import pymongo
from pymongo import MongoClient

class DBAcademic(object):
  """docstring for DBAcademic"""
  def __init__(self, type):
    client = MongoClient()
    if type == "academic":
      self.db = client['academic']
      self.collection = self.db['data_academic']
    elif type == "research":
      self.db = client['research']
      self.collection = self.db['data_research']

  def insertDoc(self, rjson):
    post_id = self.collection.update({ 'url': rjson['url'] }, rjson, upsert= True )   
    print(post_id)