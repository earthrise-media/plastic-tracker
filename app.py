import pandas as pd
import numpy as np
import altair as alt
import streamlit as st
import plotly.graph_objects as go


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


# TEST VIZ: Group the plastic conversion into a dataframe ready for Plotly
# sankey visualization
viz_links = conversion_links[conversion_links.owner.isin(top_producers[0:n_producer])]
viz_links = viz_links[viz_links.polymer == polymer].groupby(["source_country", "polymer", "country"]).sum()
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
	value  = viz_links.value
)

data = go.Sankey(link = link)
fig = go.Figure(data)


st.plotly_chart(fig, use_container_width=True)
