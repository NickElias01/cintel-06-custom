# ================================================================
# Restaurant Tipping Data Analysis App
# ================================================================
# This Shiny app allows users to interactively explore tipping data
# from a restaurant, based on various filters such as bill amount,
# time of service, gender, smoker status, day of the week, and party size.
#
# Key Features:
# - Filter data by bill amount, service time, gender, smoker status,
#   day of the week, and party size.
# - Display metrics like total sales, average tip, highest tip, and
#   lowest tip, all updated based on user-selected filters.
# - Interactive scatter plot showing the relationship between total bill
#   and tip, with a manually added line of best fit.
# - Reset all filters to their default values with a single button click.
#
# This app uses Plotly for visualizations, pandas for data manipulation,
# and Shiny for building reactive web applications in Python.
# ================================================================


import pathlib  # For handling file paths
import pandas as pd  # For data manipulation
import faicons as fa  # For FontAwesome icons
import plotly.express as px  # For creating interactive visualizations
from shinywidgets import render_plotly  # For rendering Plotly charts in Shiny
from shiny import reactive, render, req  # For reactive components and rendering in Shiny
from shiny.express import input, ui  # For creating Shiny UI components and accessing inputs
import numpy as np  # For numerical operations like polyfit

# File path to tips.csv (using pathlib to build the path)
file = pathlib.Path(__file__).parent / "tips.csv"

# Reactive file reader for CSV (this will read the CSV file reactively when needed)
@reactive.file_reader(file)
def read_file():
    return pd.read_csv(file)

# Add page title and sidebar configuration
ui.page_opts(title="Elias Analytics- Restauraunt Tipping Analysis", fillable=True)  # Set the title for the page and make it resizable
with ui.sidebar(open="desktop"):  # Create a sidebar that opens on desktop
    # Slider for selecting the bill amount range
    ui.input_slider(
        "total_bill",
        "Bill amount",
        min=10,  # Minimum value for the slider
        max=50,  # Maximum value for the slider
        value=(10, 50),  # Initial range of the slider
        pre="$",  # Prefix for the values displayed
    )
    # Checkbox group for selecting food service time (Lunch or Dinner)
    ui.input_checkbox_group(
        "time",
        "Food service",
        ["Lunch", "Dinner"],
        selected=["Lunch", "Dinner"],
        inline=True,
    )
    # Checkbox group for selecting gender
    ui.input_checkbox_group(
        "sex", "Gender", ["Male", "Female"], selected=["Male", "Female"], inline=True
    )
    # Checkbox group for selecting smoker status
    ui.input_checkbox_group(
        "smoker", "Smoker status", ["Yes", "No"], selected=["Yes", "No"], inline=True
    )
    # Checkbox group for selecting the day of the week
    ui.input_checkbox_group(
        "day",
        "Day of the week",
        ["Thur", "Fri", "Sat", "Sun"],
        selected=["Thur", "Fri", "Sat", "Sun"],
        inline=True,
    )
    # Slider for selecting party size range
    ui.input_slider("size", "Party Size", min=1, max=6, value=(1, 6), step=1)
    # Reset button to clear all filter selections
    ui.input_action_button("reset", "Reset filter")

# Add main content with icons and layout
ICONS = {
    "user": fa.icon_svg("user", "regular"),  # User icon
    "wallet": fa.icon_svg("wallet"),  # Wallet icon
    "currency-dollar": fa.icon_svg("dollar-sign"),  # Dollar sign icon
    "gear": fa.icon_svg("gear"),  # Gear icon
}

with ui.layout_columns(fill=True):  # Layout for the content with filling

    # Parent card for displaying sales metrics
    with ui.card():
        ui.card_header("Sales Summary")  # Card header for the summary

        # Nested card for displaying total sales count
        with ui.card():
            ui.card_header("Total Sales")

            @render.text
            def total_sales():
                """Display the total sales count based on the filtered data"""
                data = tips_data()  # Get the filtered data
                if data.shape[0] > 0:  # Check if data is available after filtering
                    return f"{data.shape[0]} sales"  # Display number of sales
                return "No data available"  # If no data, return this message

        # Nested card for displaying the average tip
        with ui.card():
            ui.card_header("Average Tip")

            @render.text
            def average_tip():
                """Display the average tip based on the filtered data"""
                data = tips_data()  # Get the filtered data
                if data.shape[0] > 0:
                    avg_tip = data["tip"].mean()  # Calculate average tip
                    return f"${avg_tip:.2f}"  # Display the average formatted as currency
                return "No data available"  # If no data, return this message

        # Nested card for displaying the highest tip
        with ui.card():
            ui.card_header("Highest Tip")

            @render.text
            def highest_tip():
                """Display the highest tip based on the filtered data"""
                data = tips_data()  # Get the filtered data
                if data.shape[0] > 0:
                    highest_tip = data["tip"].max()  # Find the highest tip
                    return f"${highest_tip:.2f}"  # Display the highest tip formatted as currency
                return "No data available"  # If no data, return this message

        # Nested card for displaying the lowest tip
        with ui.card():
            ui.card_header("Lowest Tip")

            @render.text
            def lowest_tip():
                """Display the lowest tip based on the filtered data"""
                data = tips_data()  # Get the filtered data
                if data.shape[0] > 0:
                    lowest_tip = data["tip"].min()  # Find the lowest tip
                    return f"${lowest_tip:.2f}"  # Display the lowest tip formatted as currency
                return "No data available"  # If no data, return this message


# Plot the scatter plot of total_bill vs tip with a manually added line of best fit
@render_plotly
def scatter_plot():
    """Plot a scatter plot of total_bill vs tip with a manually added line of best fit."""
    data = tips_data()  # Get the filtered data

    if data.shape[0] > 0:
        # Create scatter plot using Plotly
        fig = px.scatter(
            data_frame=data,
            x="total_bill",
            y="tip",
            title="Total Bill vs Tip",
            labels={"total_bill": "Total Bill ($)", "tip": "Tip ($)"},
        )

        # Add the line of best fit
        x_vals = np.array(data["total_bill"])  # Get the total bill values
        y_vals = np.array(data["tip"])  # Get the tip values

        # Calculate the slope and intercept of the line of best fit using numpy
        slope, intercept = np.polyfit(x_vals, y_vals, 1)  # Linear fit

        # Generate points for the line of best fit
        line_x = np.linspace(min(x_vals), max(x_vals), 100)
        line_y = slope * line_x + intercept

        # Add the line of best fit to the plot
        fig.add_scatter(
            x=line_x,
            y=line_y,
            mode="lines",
            name="Line of Best Fit",
            line=dict(color="red"),  # Color the line red
        )

        return fig  # Return the figure with the scatter plot and line of best fit
    else:
        return px.scatter(title="No data available")  # Return a blank plot if no data


# --------------------------------------------------------
# Reactive calculations and effects
# --------------------------------------------------------

@reactive.calc
def tips_data():
    """Filter the tips data based on user input."""
    tips = read_file()  # Read the data reactively
    bill = input.total_bill()  # Get slider values (min, max) for bill amount
    idx1 = tips["total_bill"].between(bill[0], bill[1])  # Filter by bill amount
    idx2 = tips["time"].isin(input.time())  # Filter by selected time(s)
    idx3 = tips["sex"].isin(input.sex())  # Filter by selected sex
    idx4 = tips["smoker"].isin(input.smoker())  # Filter by smoker status
    idx5 = tips["day"].isin(input.day())  # Filter by selected days
    idx6 = tips["size"].between(input.size()[0], input.size()[1])  # Filter by party size range
    return tips[idx1 & idx2 & idx3 & idx4 & idx5 & idx6]  # Return the filtered data

# Effect to reset all filters to their default state when the reset button is clicked
@reactive.effect
@reactive.event(input.reset)
def reset_filters():
    """Reset all filters to their default state."""
    ui.update_slider("total_bill", value=(10, 50))  # Reset slider for total_bill
    ui.update_checkbox_group("time", selected=["Lunch", "Dinner"])  # Reset checkbox for time
    ui.update_checkbox_group("sex", selected=["Male", "Female"])  # Reset checkbox for sex
    ui.update_checkbox_group("smoker", selected=["Yes", "No"])  # Reset checkbox for smoker
    ui.update_checkbox_group("day", selected=["Thur", "Fri", "Sat", "Sun"])  # Reset checkbox for day
    ui.update_slider("size", value=(1, 6))  # Reset slider for party size
