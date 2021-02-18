import pandas as pd
import numpy as np
import plotly.graph_objects as go
import streamlit as st

def filter_df(df, num_sources=None, num_targets=None):
    """
    A function to filter the data frame by top n sources and targets
    If num_sources or num_targets args are not supplied, they will not be filtered
    """
    if num_targets:
        top_targets = df.sum().sort_values(ascending=False)
        df = df[top_targets[:num_targets].index]

    if num_sources:
        top_sources = df.sum(axis=1).sort_values(ascending=False)[:num_sources]
        df = df.loc[top_sources.index]

    return df

def create_sankey_df(df, min_val=0):
    """
    Create the human-readable form of the Sankey chart data from an input data frame
    Data can be filtered by a threshold minimum value
    | Source | Source Value | Target | Target Value |
    |    A   |      5       |   i    |      3       |
    |    A   |      5       |   j    |      2       |
    |    B   |      7       |   i    |      1       |
    |    B   |      7       |   k    |      4       |
    """

    sources = []
    source_vals = []
    targets = []
    target_vals = []
    for source_name in df.index:
        row = df.loc[source_name]
        sources += [source_name] * sum(row.values > min_val)
        source_vals += [row[row.values > min_val].sum()] * sum(row.values > min_val)
        targets += list(row[row > min_val].index)
        target_vals += list(row[row > min_val].values)

    sankey_df = pd.DataFrame({
        'source': sources,
        'source_value': source_vals,
        'target': targets,
        'target_value': target_vals
    })

    return sankey_df

def create_sankey_dict(sankey_df):
    """
    Plotly requires that each source and target be converted to a numerical index
    This index also points to an entry in the labels file
    As a convention that I think will be useful, indices for a target build off of
    the last value in the preceding column's indices
    """
    source_nodes = sorted(sankey_df.source.unique())
    source_node_dict = {source_nodes[i]: i for i in range(len(source_nodes))}

    target_nodes = sorted(sankey_df.target.unique())
    target_node_dict = {target_nodes[i]: i + max(source_node_dict.values()) + 1 for i in range(len(target_nodes))}

    source_indices = list(sankey_df.source.map(source_node_dict).values)
    source_values  = list(sankey_df.source_value)
    target_indices = list(sankey_df.target.map(target_node_dict).values)
    target_values  = list(sankey_df.target_value)

    sankey_dict = {
        'source_labels': source_nodes,
        'source': source_indices,
        'source_values': source_values,
        'target_labels': target_nodes,
        'target': target_indices,
        'target_values': target_values
    }

    return sankey_dict

def plot_sankey(sankey_dict, title):
    """Plot a Sankey diagram. By default, line height is given by the target values"""
    # Figure configuration

    layout = go.Layout(
    	paper_bgcolor = 'rgb(228, 218, 204)',
    	plot_bgcolor = 'rgb(228, 218, 204)'
    )
    fig = go.Figure(data=[go.Sankey(
        node = dict(
          pad = 15,
          thickness = 20,
          line = dict(color = "black", width = 0.5),
          label = sankey_dict['source_labels'] + sankey_dict['target_labels'],
          color = "black"
        ),
        link = dict(
          source = sankey_dict['source'],
          target = sankey_dict['target'],
          value  = sankey_dict['target_values']
      ))], layout=layout)

    fig.update_layout(title_text=title, font_size=10)
    return fig

@st.cache(persist=True)
def load_data():

    investor = pd.read_excel(
        "./data/Equity investor SUP matrix.xlsx",
        engine="openpyxl",
        skiprows=3,
        usecols="B, E:GG",
    )
    investor = investor.rename(columns={investor.columns[0]: "Ultimate Investor"})
    # drop last row because it is a table summary
    investor = investor[:-1]
    investor = investor.set_index('Ultimate Investor')

    financer = pd.read_excel(
        "./data/Financing SUP matrix.xlsx",
        engine="openpyxl",
        skiprows=4,
        usecols="A:AV",
    )

    # drop last row because it is null
    financer = financer[:-1]
    financer = financer.set_index('Bank')

    producer = pd.read_excel(
        "./data/MFA matrix.xlsx",
        sheet_name="Conversion",
        engine="openpyxl",
        skiprows=1,
        usecols="C:FY",
    ).dropna()
    producer = producer.groupby('Producer').sum()

    waste = pd.read_excel(
        "./data/MFA matrix.xlsx",
        sheet_name="Waste",
        engine="openpyxl",
        skiprows=1,
        usecols="B, D:FY",
    ).dropna()

    waste = waste.groupby('Country').sum()

    return investor, financer, producer, waste

st.header("Global Plastic Polluters Index")
investor, financer, producer, waste = load_data()
plot_config = {'displayModeBar': False}

st.markdown("""
PPI Node 1-2: Financer OR Investor to Producer
""")

financing_type = st.selectbox(
	'Financing type',
	['Investor', 'Financer']
)


if financing_type == 'Financer':
    n_money_sources = st.slider(
    	'Number of top funding sources to visualize',
    	1, len(financer), 10
    )
    n_producer_targets = st.slider(
    	'Number of top producers to visualize',
    	1, len(financer.columns), 10
    )
    minimum_financing_value = st.slider(
    	'Threshold for minimum funding value',
    	0, int(financer.max().max()), 500
    )
    financer_df = filter_df(financer, num_sources=n_money_sources, num_targets=n_producer_targets)
    financer_sankey_df = create_sankey_df(financer_df, min_val=minimum_financing_value)
    financer_sankey_dict = create_sankey_dict(financer_sankey_df)
    financer_plot = plot_sankey(financer_sankey_dict, 'Financer to Producer')
    st.plotly_chart(financer_plot, use_container_width=True, config=plot_config)

if financing_type == 'Investor':
    n_money_sources = st.slider(
    	'Number of top funding sources to visualize',
    	1, len(investor), 10
    )
    n_producer_targets = st.slider(
    	'Number of top producers to visualize',
    	1, len(investor.columns), 10
    )
    minimum_financing_value = st.slider(
    	'Threshold for minimum funding value',
    	0, int(investor.max().max()), 100
    )
    investor_df = filter_df(investor, num_sources=n_money_sources, num_targets=n_producer_targets)
    investor_sankey_df = create_sankey_df(investor_df, min_val=minimum_financing_value)
    investor_sankey_dict = create_sankey_dict(investor_sankey_df)
    investor_plot = plot_sankey(investor_sankey_dict, 'Investor to Producer')
    st.plotly_chart(investor_plot, use_container_width=True, config=plot_config)

st.markdown("""
PPI Node 2-3: Producer to Country of Production
""")

n_producer_sources = st.slider(
	'Number of top producers to visualize',
	1, len(producer), 10
)
n_country_targets = st.slider(
	'Number of top countries to visualize',
	1, len(producer.columns), 10
)
minimum_production_value = st.slider(
	'Threshold for minimum production volume',
	0, int(producer.max().max()), 1500
)
producer_df = filter_df(producer, num_sources=n_producer_sources, num_targets=n_country_targets)
producer_sankey_df = create_sankey_df(producer_df, min_val=minimum_production_value)
producer_sankey_dict = create_sankey_dict(producer_sankey_df)
producer_plot = plot_sankey(producer_sankey_dict, 'Producer to Country of Production')
st.plotly_chart(producer_plot, use_container_width=True, config=plot_config)


st.markdown("""
PPI Node 3-4: Country of Production to Country of Impact
""")

n_country_sources = st.slider(
	'Number of top producing countries to visualize',
	1, len(waste), 10
)
n_waste_targets = st.slider(
	'Number of top destination countries to visualize',
	1, len(waste.columns), 10
)
minimum_waste_value = st.slider(
	'Threshold for minimum waste volume',
	0, int(waste.max().max()), 1000
)

waste_df = filter_df(waste, num_sources=n_country_sources, num_targets=n_waste_targets)
waste_sankey_df = create_sankey_df(waste_df, min_val=minimum_waste_value)
waste_sankey_dict = create_sankey_dict(waste_sankey_df)
waste_plot = plot_sankey(waste_sankey_dict, 'Country of Production to Country of Impact')
st.plotly_chart(waste_plot, use_container_width=True, config=plot_config)
