import plotly.plotly as py
from plotly.graph_objs import *

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from tdb_tables import Habitat

Base = declarative_base()
engine = create_engine('sqlite:///telanganadb_salchemy.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

x_data = []
mandal_y_data = []
panchayat_y_data = []
districts = session.query(Habitat).filter(Habitat.type=="District").all()
for district in districts:
	x_data.append(district.name)
	mandal_count = session.query(Habitat).filter(Habitat.type=="Mandal",Habitat.district_code==district.code).count()
	panchayat_count = session.query(Habitat).filter(Habitat.type=="Panchayat",Habitat.district_code==district.code).count()
	mandal_y_data.append(mandal_count)
	panchayat_y_data.append(panchayat_count)


trace1 = Scatter(
    x=x_data,
    y=mandal_y_data,
    name='Mandals'
)
trace2 = Scatter(
    x=x_data,
    y=panchayat_y_data,
    name='GramPanchayats',
    yaxis='y2'
)

data = Data([trace1,trace2])
layout = Layout(
	title='Telangana Habitat Graph',

	yaxis=YAxis(
        title='Mandals',
        titlefont=Font(color='rgb(148, 103, 189)'),
    ),

    yaxis2=YAxis(
        title='Grampanchayats',
        titlefont=Font(
            color='rgb(148, 103, 189)'
        ),
        tickfont=Font(
            color='rgb(148, 103, 189)'
        ),
        overlaying='y',
        side='right'
    )
)

fig = Figure(data=data, layout=layout)
plot_url = py.plot(fig, filename='Telangana Districts vs Mandals')
