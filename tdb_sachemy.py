import requests
from lxml import html
from lxml import etree
import threading

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from tdb_tables import Habitat

Base = declarative_base()

engine = create_engine('sqlite:///telanganahabitatdb.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

govt_url="http://tspri.cgg.gov.in/Ajax.do"

db_lock = threading.Lock()

districts = { 
	'14': 'Mahabubnagar' ,
	'15': 'Ranga Reddy' ,
	'17': 'Medak' ,
	'18': 'Nizamabad' ,
	'19': 'Adilabad' ,
	'20': 'Karimnagar' ,
	'21': 'Warangal' ,
	'22': 'Khammam' ,
	'23': 'Nalgonda' ,
	}


def insert_into_db(code, type, name, panchayat_code, mandal_code,district_code):
	db_lock.acquire()
	new_habitat = Habitat(code=code,name=name,type=type,\
		panchayat_code=panchayat_code,mandal_code=mandal_code,district_code=district_code)
	session.add(new_habitat)
	session.commit()
	db_lock.release()

def process_districts():
	for dt_code,dt_name in districts.iteritems():
		insert_into_db(code=dt_code,name=dt_name,type="District",panchayat_code="",\
			mandal_code="",district_code="")

def clean_database():
	session.query(Habitat).delete()

def get_districts():
	districts = session.query(Habitat).filter(Habitat.type=="District").all()
	return districts

def get_mandals():
	mandals = session.query(Habitat).filter(Habitat.type=="Mandal").order_by(Habitat.district_code)
	return mandals

def get_panchayats():
	panchayats = session.query(Habitat).filter(Habitat.type=="Panchayat").order_by(Habitat.mandal_code,Habitat.district_code)
	return panchayats

def process_mandals(district_code):
	for district in get_districts():
		mandal_payload = {'district': district.code, 'key': 'getMandals','tagname':'mandal'}
		page = requests.post(govt_url, data=mandal_payload)
		md_xml = etree.fromstring(page.content)
		for md in md_xml.xpath("//mandal"):
			insert_into_db(code=md.attrib["id"],name=md.attrib["name"],type="Mandal",\
				panchayat_code="",mandal_code="",district_code=district.code)

def process_panchayats():
	for mandal in get_mandals():
		panchayat_payload = {'district': mandal.district_code, 'mandal': mandal.code, \
		'key': 'getPanchayats','tagname': 'panchayat'} 
		page = requests.post(govt_url, data=panchayat_payload)
		panchayat_xml = etree.fromstring(page.content)
		for pc in panchayat_xml.xpath("//panchayat"):
			insert_into_db(code=pc.attrib["id"],name=pc.attrib["name"],type="Panchayat",\
				panchayat_code="",mandal_code=mandal.code,district_code=mandal.district_code)

def process_villages():
	for panchayat in get_panchayats():
		village_payload = {'district': panchayat.district_code, 'mandal': panchayat.mandal_code, 'panchayat':panchayat.code,'key': 'getVillages','tagname': 'village'}
		page = requests.post(govt_url, data=village_payload)
		village_xml = etree.fromstring(page.content)
		for vil in village_xml.xpath("//village"):
			insert_into_db(code=vil.attrib["id"],name=vil.attrib["name"],type="Village",\
				panchayat_code=panchayat.code,mandal_code=panchayat.mandal_code,\
				district_code=panchayat.district_code)

def process_by_district(district_code):
	mandal_payload = {'district': district_code, 'key': 'getMandals','tagname':'mandal'}
	page = requests.post(govt_url, data=mandal_payload)
	md_xml = etree.fromstring(page.content)
	for md in md_xml.xpath("//mandal"):
		insert_into_db(code=md.attrib["id"],name=md.attrib["name"],type="Mandal",\
				panchayat_code="",mandal_code="",district_code=district_code)
		panchayat_payload = {'district': district_code, 'mandal': md.attrib["id"], \
		'key': 'getPanchayats','tagname': 'panchayat'} 
		page = requests.post(govt_url, data=panchayat_payload)
		panchayat_xml = etree.fromstring(page.content)
		for pc in panchayat_xml.xpath("//panchayat"):
			insert_into_db(code=pc.attrib["id"],name=pc.attrib["name"],type="Panchayat",\
				panchayat_code="",mandal_code=md.attrib["id"],district_code=district_code)
			village_payload = {'district': district_code, 'mandal': md.attrib["id"],\
			 'panchayat':pc.attrib["id"],'key': 'getVillages','tagname': 'village'}
			page = requests.post(govt_url, data=village_payload)
			village_xml = etree.fromstring(page.content)
			for vil in village_xml.xpath("//village"):
				insert_into_db(code=vil.attrib["id"],name=vil.attrib["name"],type="Village",\
				panchayat_code=pc.attrib["id"],mandal_code=md.attrib["id"],\
				district_code=district_code)


if __name__ == '__main__':
	clean_database()
	process_districts()
	threads = []
	for dt_code, dt_name in districts.iteritems():
		t = threading.Thread(target=process_by_district,args=(dt_code,))
		threads.append(t)
		t.start()


	# process_mandals()
	# process_panchayats()
	# process_villages()
	# select_all()