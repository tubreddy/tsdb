import requests
from lxml import html
from lxml import etree
import threading

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from tsdb_tables import Habitat

Base = declarative_base()

engine = create_engine('sqlite:///telanganadb_salchemy.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

govt_url="http://tspri.cgg.gov.in/Ajax.do"

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

def process_districts():
	for dt_code,dt_name in districts.iteritems():
		new_habitat = Habitat(code=dt_code,name=dt_name,type="District")
		session.add(new_habitat)
	session.commit()

def clean_database():
	session.query(Habitat).delete()

def select_all():
	districts=session.query(Habitat).filter(Habitat.type=="District").all()
	for dt in districts:
		print dt.code

def get_districts():
	districts = session.query(Habitat).filter(Habitat.type=="District").all()
	return districts

def get_mandals():
	mandals = session.query(Habitat).filter(Habitat.type=="Mandal").order_by(Habitat.district_code)
	return mandals

def get_panchayats():
	panchayats = session.query(Habitat).filter(Habitat.type=="Panchayat").order_by(Habitat.mandal_code,Habitat.district_code)
	return panchayats

def process_mandals():
	for district in get_districts():
		mandal_payload = {'district': district.code, 'key': 'getMandals','tagname':'mandal'}
		page = requests.post(govt_url, data=mandal_payload)
		md_xml = etree.fromstring(page.content)
		for md in md_xml.xpath("//mandal"):
			new_habitat = Habitat(code=md.attrib["id"],name=md.attrib["name"],type="Mandal",district_code=district.code)
			session.add(new_habitat)
		session.commit()

def process_panchayats():
	for mandal in get_mandals():
		panchayat_payload = {'district': mandal.district_code, 'mandal': mandal.code, \
		'key': 'getPanchayats','tagname': 'panchayat'} 
		page = requests.post(govt_url, data=panchayat_payload)
		panchayat_xml = etree.fromstring(page.content)
		for pc in panchayat_xml.xpath("//panchayat"):
			new_habitat = Habitat(code=pc.attrib["id"],name=pc.attrib["name"],type="Panchayat", mandal_code=mandal.code,district_code=mandal.district_code)
			session.add(new_habitat)
		session.commit()

def process_villages():
	for panchayat in get_panchayats():
		village_payload = {'district': panchayat.district_code, 'mandal': panchayat.mandal_code, 'panchayat':panchayat.code,'key': 'getVillages','tagname': 'village'}
		page = requests.post(govt_url, data=village_payload)
		village_xml = etree.fromstring(page.content)
		for vil in village_xml.xpath("//village"):
			new_habitat = Habitat(code=vil.attrib["id"],name=vil.attrib["name"],type="Village", mandal_code=panchayat.mandal_code,district_code=panchayat.district_code)
			session.add(new_habitat)
		session.commit()


if __name__ == '__main__':
	clean_database()
	process_districts()
	process_mandals()
	process_panchayats()
	process_villages()
	select_all()
