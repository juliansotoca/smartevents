#!/usr/bin/env python
#encoding:utf-8

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#
# Julian Garcia-Sotoca Pascual


from pymongo import Connection

conn = Connection()
db = conn.events
coll = db.events
#definicion elemento
e1={'body': "04", 'status': 'Open', 'domain': 'Servicios', 'option': 'message', 'url': '', 'user': '', 'id': '5327325', 'criticalness': 'warning', 'dateTime': '2014-06-17 18:24:34'}
e2={'body': u'04 - Servicios\\\\WIS - Venta Excursiones TPV\n\n--- COMPONENTES RECUPERADOS (2) ---\n\n1.P11 - Sesiones activas\n\n2.P11 - Alcance procesos\n', 'status': 'Open', 'domain': 'Servicios', 'option': 'message', 'url': '', 'user': '', 'id': '5327324', 'criticalness': 'success', 'dateTime': '2014-06-17 18:24:34'}
#insertar elemento
#mongo_id=coll.insert(e1)
#print mongo_id
#mongo_id=coll.insert(e2)
#print mongo_id
#buscar un documento
coll.find_one({'domain': 'Servicios'})
#buscar todos los documentos e imprimir un campo
for event in coll.find():
	print event
	
#Actualizar un documento
#coll.update({'id': '532732'}, {"$set": {'status': 'closed'}}, upsert=True)

#updated = coll.find_one({'id': '5327324'})
#print "updated %s" % updated['status']
#print "closed: %d" % coll.find({'status': 'closed'}).count()
#print "open: %d" % coll.find({'status': 'Open'}).count()
	
#contar Documentos	
print "all documents: %d" % coll.count()
print "documents domain servicios: %d" %coll.find({'domain': 'Servicios'}).count()

#Borrar elemento
#coll.remove({'status': 'closed'})
#print "all documents: %d" % coll.count()
