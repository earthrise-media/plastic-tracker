import pandas as pd
import numpy as np
import altair as alt
import streamlit as st
import plotly.graph_objects as go
import geopandas

from PIL import Image

st.header("Global Plastic Polluters Index")


st.markdown("""

The mission of Minderoo Foundation’s **Sea the Future** initiative is to eliminate
the negative impacts of plastic waste, with twin goals: end plastic leakage to
nature, and accelerate the transition to a circular plastics economy.

We believe in creating greater transparency across the plastics value chain –
of financial and material flows and impacts – to engender greater
accountability and result in positive changes in corporate, capital markets
and regulatory behaviour.

As an opening cry in a longer-term strategy, we plan to create, validate and
publish, for the first time, a definitive list of the global producers
responsible for “fast moving” plastic packaging polymers (PE, PP, PET). These
polymers account for the majority of mismanaged plastic waste and plastic
leaking into nature.

> _The objective of this web app is to provide a platform to collaborate with
the Minderoo team to design the data interactions that would be most useful.
It is not a draft visualization, just a way to potentially communicate across
teams._

The design mocks, displayed below, illustrate the flow of plastics &mdash;
from dollars to polymers to plastic waste.

""")


image = Image.open('imgs/screen.png')

st.image(
	image, 
	use_column_width=True
)


st.markdown("""

	The following visualization is an incremental illustration of how to go from
	real data to the intended visualization.  **Note that you can expand the
	visualization using the fullscreen button in the top-right corner.**

""")

@st.cache(persist=True)
def load_data(plot=True):
	# Cache the datasets that we rely on, so we don't have to reload them over
	# and over again each time a parameter changes
	production_df = pd.read_pickle("dataframes/production.pkl")
	top_producers = production_df.groupby(["Operator"]).sum().reset_index()
	top_producers = top_producers[["Operator", "2019 Production"]].sort_values(
		by=["2019 Production"], ascending=False
	)
	
	top_producers = top_producers["Operator"].to_list()

	return {
		"top_producers": top_producers,
		"resin_trade": pd.read_pickle("dataframes/resin_trade_links.pkl"),
		"conversion_trade": pd.read_pickle("dataframes/conversion_links.pkl")
	}

data = load_data()
resin_links = data["resin_trade"]
top_producers = data["top_producers"]
conversion_links = data["conversion_trade"]

# Selection of visualization options

polymer = st.selectbox(
	'Polymer type',
	['LDPE', 'LLDPE', 'HDPE', 'PP', 'PET']
)

n_producer = st.slider(
	'Number of top producers to visualize',
	5, 30, 10
)

min_tradeval = st.slider(
	'Minimum number of kilotons to include in trade links',
	1, 50, 30
)


st.markdown(""" 

	The first Sankey diagram plots the connection between the country that has
	converted the polymer to the final destination of the single-use plastics. 
	Note that there are a few loops &mdash; where a country will both produce and
	consume the single-use plastics.  This does not qualify as an "alluvial"
	Sankey diagram, and would not be suitable for the final visualization. The
	visualization is pretty cool, even without the country labels.

""")

viz_links = conversion_links[conversion_links.owner.isin(top_producers[0:n_producer])]
viz_links = viz_links[viz_links.polymer == polymer]
viz_links = viz_links.groupby(["source_country", "polymer", "country"]).sum()
viz_links = viz_links[viz_links.tradeval > min_tradeval].reset_index()

countries = set(viz_links.source_country).union(set(viz_links.country))
nodes = sorted(list(countries))
node_dict = {nodes[i]: i for i in range(len(nodes))}
viz_links["source"] = viz_links.source_country.map(node_dict)
viz_links["target"] = viz_links.country.map(node_dict)
viz_links["value"]  = viz_links.tradeval

labels = list(node_dict.keys())

link = dict(
	source = viz_links.source, 
	target = viz_links.target, 
	value  = viz_links.value,
	hoverlabel = dict(
		bordercolor='rgb(228, 218, 204)',
		bgcolor = 'rgb(228, 218, 204)',
		font = dict(
			family="Open Sans",
			size=12,
			color='rgb(68, 68, 68)'
		)
	),
	label=labels
)

node=dict(
	# Put in default that is overwritten by the "none"
	hoverinfo="none",
	pad=15,
	thickness=20,
	line=dict(
		color="black",
		width=0.5
	),
	hoverlabel = dict(
		bordercolor='rgb(228, 218, 204)',
		bgcolor = 'rgb(228, 218, 204)',
		font = dict(
			family="Open Sans",
			size=12,
			color='rgb(68, 68, 68)'
		)
	)
)

data = go.Sankey(link=link, node=node)

# Configurations
config = {'displayModeBar': False}
layout = go.Layout(
	paper_bgcolor = 'rgb(228, 218, 204)',
	plot_bgcolor = 'rgb(228, 218, 204)'
)

fig = go.Figure(data=data, layout=layout)

fig.update_layout(
    font=dict(size = 30, color = 'white')
)

st.plotly_chart(fig, config=config, use_container_width=True)

st.markdown(""" 

	The data has to be reassembled to support a linear flow diagram (i.e.,
	indicating a flow from left to right).

""")

viz_links = conversion_links[conversion_links.owner.isin(top_producers[0:n_producer])]
viz_links = viz_links[viz_links.polymer == polymer].groupby(["source_country", "polymer", "country"]).sum()
viz_links = viz_links[viz_links.tradeval > min_tradeval].reset_index()

source = sorted(list(set(viz_links.source_country)))
target = sorted(list(set(viz_links.country)))

source_node_dict = {source[i]: i for i in range(len(source))}
target_node_dict = {target[i]: i + len(source) for i in range(len(target))}

viz_links["source"] = viz_links.source_country.map(source_node_dict)
viz_links["target"] = viz_links.country.map(target_node_dict)
viz_links["value"]  = viz_links.tradeval

labels = source + target

link = dict(
	source = viz_links.source, 
	target = viz_links.target, 
	value  = viz_links.value,
	hoverlabel = dict(
		bordercolor='rgb(228, 218, 204)',
		bgcolor = 'rgb(228, 218, 204)',
		font = dict(
			family="Open Sans",
			size=12,
			color='rgb(68, 68, 68)'
		)
	),
	label=labels
)

node=dict(
	# Put in default that is overwritten by the "none"
	hoverinfo="none",
	pad=15,
	thickness=20,
	line=dict(
		color="black",
		width=0.5
	),
	hoverlabel = dict(
		bordercolor='rgb(228, 218, 204)',
		bgcolor = 'rgb(228, 218, 204)',
		font = dict(
			family="Open Sans",
			size=12,
			color='rgb(68, 68, 68)'
		)
	)
)

data = go.Sankey(link=link, node=node)

# Configurations
config = {'displayModeBar': False}
layout = go.Layout(
	paper_bgcolor = 'rgb(228, 218, 204)',
	plot_bgcolor = 'rgb(228, 218, 204)'
)

fig = go.Figure(data=data, layout=layout)

fig.update_layout(
    font=dict(size = 30, color = 'white')
)

st.plotly_chart(fig, config=config, use_container_width=True)


st.markdown("""

	The major issue will be the units when stringing the data together.  It is
	unclear how to track the input from a polymer producer through to the
	plastics at the final destination &mdash; which have multiple inputs which
	still translate into traded weight.

""")


second_link = resin_links[resin_links.owner.isin(top_producers[0:n_producer])]
second_link = second_link[second_link.polymer == polymer].groupby(["owner", "polymer", "country"]).sum()
second_link = second_link[second_link.tradeval > min_tradeval].reset_index()

b_nodes = sorted(list(
    set(second_link.owner)
))

# The target for the second link is the source for third (and final) link
c_nodes = sorted(list(
    set(second_link.country)
))

b_node_dict = {b_nodes[i]: i for i in range(len(b_nodes))}
c_node_dict = {c_nodes[i]: i + len(b_nodes) for i in range(len(c_nodes))}


second_source = second_link.owner.map(b_node_dict)
second_target = second_link.country.map(c_node_dict)

viz_links = pd.DataFrame.from_dict({
    "source": second_source,
    "target": second_target, 
    "value" : second_link.tradeval
})


third_link = conversion_links[conversion_links.source_country.isin(c_nodes)]
third_link = third_link[third_link.polymer == polymer].groupby(["source_country", "polymer", "country"]).sum()
third_link = third_link[third_link.tradeval > min_tradeval].reset_index()

d_nodes = sorted(list(
    set(third_link.country)
))

d_node_dict = {d_nodes[i]: i + len(b_nodes) + len(c_nodes) for i in range(len(d_nodes))}

third_source = third_link.source_country.map(c_node_dict)
third_target = third_link.country.map(d_node_dict)

viz_links_b = pd.DataFrame.from_dict({
    "source": third_source,
    "target": third_target, 
    "value" : third_link.tradeval
})

viz_links = viz_links.append(viz_links_b, ignore_index=True)

labels = b_nodes + c_nodes + d_nodes

fig = go.Figure(
	data=[go.Sankey(
		node = dict(
			pad = 15,
			thickness = 30,
			line = dict(color = "black", width = 0.5),
			label = labels,
			color = "#303030",
			hoverlabel = dict(
				bordercolor='rgb(228, 218, 204)',
				bgcolor = 'rgb(228, 218, 204)',
				font = dict(
					family="Open Sans",
					size=12,
					color='rgb(68, 68, 68)'
				)
			)
		),
		link = dict(
			source = viz_links.source,
			target = viz_links.target,
			value = viz_links.value,
			hoverlabel = dict(
				bordercolor='rgb(228, 218, 204)',
				bgcolor = 'rgb(228, 218, 204)',
				font = dict(
					family="Open Sans",
					size=12,
					color='rgb(68, 68, 68)'
				)
			)
		)
	)],
	layout=layout
)

st.plotly_chart(fig, config=config, use_container_width=True)

st.markdown(""" The location of the assets **may** help filter the nodes in
the Sankey diagram. """)

image = Image.open('imgs/assets.png')

st.image(
	image, 
	use_column_width=True
)