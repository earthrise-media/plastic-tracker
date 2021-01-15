import pandas as pd
import numpy as np
import altair as alt
import streamlit as st

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

from PIL import Image
image = Image.open('imgs/screen.png')

st.image(
	image, 
	caption='Flow diagram', 
	use_column_width=True
)


# rankings = pd.read_csv("data/rankings.tsv", sep="\t")
# data = pd.read_csv("data/data_table.tsv", sep="\t").astype({'2019 Production': 'float'})

# st.subheader("Top polluters")

# polymers = set(data["Polymer"])

# polymer_option = st.selectbox(
# 	"Select polymer",
# 	list(polymers)
# )

# agg_option = st.selectbox(
# 	"Select unit",
# 	["Country", "Owner Name"]
# )

# df = data[data["Polymer"] == polymer_option]
# top = df.groupby(agg_option)["2019 Production"].sum().reset_index()
# top_sorted = top.sort_values("2019 Production", ascending=False)
# nrow, ncol = top_sorted.shape


# rank_num = st.slider('Number of countries to visualize', 2, nrow, 15)

# c = alt.Chart(top_sorted[0:rank_num]).mark_bar().encode(
#     x=alt.X('2019 Production:Q', title="2019 Production (kt)"),
#     y=alt.Y('%s:N' % agg_option, sort='-x', title=" ")
# ).properties(
# 	height=int(10*rank_num + 80)
# ).configure_view(strokeOpacity=0)

# st.altair_chart(c, use_container_width=True)



# st.subheader("Underutilized capacity")

# df["2019 Capacity"] = df["2019 Capacity"] * df["Owner %"]
# cap = df.groupby(agg_option)["2019 Production", "2019 Capacity"].sum().reset_index()
# cap_sorted = cap.sort_values("2019 Capacity", ascending=False)[0:rank_num]
# cap_sorted = cap_sorted[cap_sorted["2019 Capacity"] > cap_sorted["2019 Production"]]
# cap_sorted["Extra capacity"] = cap_sorted["2019 Capacity"] - cap_sorted["2019 Production"]

# a = cap_sorted[[agg_option, "2019 Production"]]
# a["type"] = "Production"
# a.columns = [agg_option, "polymer", "t"]

# b = cap_sorted[[agg_option, "Extra capacity"]]
# b["type"] = "Extra capacity"
# b.columns = [agg_option, "polymer", "t"]

# c = alt.Chart(a.append(b)).mark_bar().encode(
#     x=alt.X('sum(polymer)', title="2019 (kt)"),
#     y=alt.Y('%s:N' % agg_option, sort='-x', title=" "),
#     color=alt.Color('t', legend=alt.Legend(title=" ", orient="top"))
# ).properties(
# 	height=int(10*rank_num + 80)
# ).configure_view(strokeOpacity=0)

# total_excess_capacity = '{:,}'.format(int(np.sum(b["polymer"])))

# if polymer_option == "PET":
# 	us_polymer = np.sum(df[df["Country"] == "US"]["2019 Production"])
# else:
# 	us_polymer = np.sum(df[df["Country"] == "United States"]["2019 Production"])

# st.markdown("""

# Some of the production assets are not producing at capacity.  The total excess
# capacity of %s in 2019 was **%s kilotons**.  For reference, the total
# production of %s in 2019 in the United States was %s kilotons.  This
# represents the capacity for production that was not used, which possibly has
# policy implications (e.g., geographic or temporal substitution).

# > _Note that there are some data issues where production exceeds capacity, but
# only rarely. These cases have been dropped until further review._

# """ % (
# 		polymer_option, 
# 		total_excess_capacity, 
# 		polymer_option, 
# 		'{:,}'.format(int(us_polymer))
# 	)
# )

# st.altair_chart(c, use_container_width=True)


# st.subheader("Linkages")

# st.markdown("""

# Countries with common investments in polymer-producing companies.  The measure
# of 2019 production corresponds to their ownership share in the company for %s.

# """ % polymer_option)


# linkdata = df.groupby(["Owner Name", "Country"])["2019 Production"].sum().reset_index()
# linkdata['count'] = linkdata.groupby('Owner Name')['Owner Name'].transform('count')
# x = linkdata[linkdata['count'] > 1].reset_index()
# st.write(x[["Owner Name", "Country", "2019 Production"]])



# st.subheader("Incoming polluters")

# st.markdown(""" 

# Some owners of polymer-producing assets were not associated with any
# production in 2019, but are expected to have a substantial polymer output by
# 2025.  This represents _all_ polymers, not just the selection.

# """)

# incoming = rankings[rankings["Sum of 2019 Production"] == 0]
# incoming_sorted = incoming.sort_values("Sum of 2025 Production", ascending=False)


# rank_num = st.slider('Number of Owners to visualize', 2, 77, 15)

# x = incoming_sorted[0:rank_num]

# c = alt.Chart(x).mark_bar().encode(
#     x=alt.X('Sum of 2025 Production:Q', title="Sum of 2025 Production (kt)"),
#     y=alt.Y('Owner Name:N', sort='-x', title=" ")
# ).properties(
# 	height=int(10*rank_num + 60)
# ).configure_view(strokeOpacity=0)

# st.altair_chart(c, use_container_width=True)