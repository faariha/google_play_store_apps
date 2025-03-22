# python -m venv myenv
# myenv\Scripts\activate
# streamlit run google_play_analysis.py


import streamlit as st
import pandas as pd
import plotly.express as px

# Load the dataset
apps_df = pd.read_csv('googleplaystore.csv')

# Remove duplicate rows in both datasets if any
apps_df.drop_duplicates(inplace=True)

# Ensure 'Last Updated' is in datetime format
apps_df['Last Updated'] = pd.to_datetime(apps_df['Last Updated'], errors='coerce')

# Calculate the median rating (ignoring missing values)
median_rating = apps_df['Rating'].median()

# Fill missing ratings with the median
apps_df['Rating'] = apps_df['Rating'].fillna(median_rating)

# Drop rows where 'Type', 'Content Rating', 'Current Ver', or 'Android Ver' are missing
apps_df = apps_df.dropna(subset=['Type', 'Content Rating', 'Current Ver', 'Android Ver'])

# Clean the 'Price' column to ensure it's numeric
apps_df['Price'] = apps_df['Price'].replace('[\$,]', '', regex=True)  # Remove '$' and ','
apps_df['Price'] = pd.to_numeric(apps_df['Price'], errors='coerce')  # Convert to numeric, invalid parsing will be set to NaN

# Handle NaN values in Price by filling with 0 
apps_df['Price'] = apps_df['Price'].fillna(0)

# Clean 'Size' column to ensure it is numeric
def parse_size(size):
    if isinstance(size, str):
        size = size.lower().replace('m', '').replace('k', '').strip()
        try:
            size = float(size)
        except ValueError:
            return None
    return size

apps_df['Size'] = apps_df['Size'].apply(parse_size)


# Clean 'Installs' column: remove characters like ',' and '+' then convert to numeric
def clean_installs(installs):
    installs = installs.replace(',', '').replace('+', '')
    try:
        return int(installs)
    except:
        return np.nan

apps_df['Installs'] = apps_df['Installs'].apply(clean_installs)

# Ensure 'Reviews' column is numeric
apps_df['Reviews'] = pd.to_numeric(apps_df['Reviews'], errors='coerce')  # Coerce errors to NaN

# Optional: Fill NaN values with 0 or drop them based on your use case
apps_df['Reviews'] = apps_df['Reviews'].fillna(0)  # Fill NaN values with 0

# Now, you can safely calculate the median of 'Reviews'
high_reviews_apps = apps_df[apps_df['Reviews'] > apps_df['Reviews'].median()]







# Sidebar for navigation
st.sidebar.title('Navigation')
page = st.sidebar.radio('Select a page:', ['Home', 'Time Series Analysis', 'Game', 'Communication', 'Social'])

# Home Page
if page == 'Home':
    st.title('Google Play Store Apps Analysis')
    
    # Display a subheader for the dataset preview
    st.subheader('Dataset Preview (First 10 Rows)')

    # Show the first 10 rows of the dataset in a table format
    st.dataframe(apps_df.head(10))  # Show the first 10 rows of the dataset

    st.header('Categorization of Apps Based on Analysis')

    # Top 10 most installed apps
    top10_installs = apps_df.sort_values(by='Installs', ascending=False).head(10)
    st.subheader('Top 10 Most Installed Apps')
    st.write(top10_installs[['App', 'Installs']])

    # Top 10 most rated apps
    top10_rated = apps_df.sort_values(by='Rating', ascending=False).head(10)
    st.subheader('Top 10 Highest Rated Apps')
    st.write(top10_rated[['App', 'Rating']])






    # Insight about Reviews and Ratings
    st.subheader('Insight: High Reviews and Good Ratings')

    # Find apps with high reviews and good ratings vs low reviews and high ratings
    high_reviews_apps = apps_df[apps_df['Reviews'] > apps_df['Reviews'].median()]
    high_rated_apps = apps_df[apps_df['Rating'] > 4]

    # Combine both conditions for high-rated and high-reviewed apps
    reliable_apps = high_reviews_apps[high_reviews_apps['Rating'] > 4]
    
    # Combine both conditions for high-rated but low-reviewed apps
    unreliable_apps = apps_df[(apps_df['Reviews'] < apps_df['Reviews'].median()) & (apps_df['Rating'] > 4)]

    # Show insights based on Install Count
    st.write("The decision of whether an app is good or not can be further validated by its **install count**. "
             "Apps with a high install count are more likely to be trustworthy, as they have been tested by a larger audience.")
    
    # --- Graph 1: Top 10 High Rated Apps with High Number of Reviews ---
    top_high_reviewed_apps = reliable_apps.nlargest(10, 'Rating')
    
    fig1 = px.scatter(
        top_high_reviewed_apps,
        x='App',
        y='Rating',
        size='Reviews',
        color='Rating',
        hover_data={'Installs': True},
        title="Top 10 High Rated Apps with High Number of Reviews",
        labels={'App': 'App Name', 'Rating': 'Rating'},
    )
    fig1.update_layout(
        xaxis_title="App Name",
        yaxis_title="Rating",
        xaxis_tickangle=-45,
        template='plotly_white'
    )
    st.plotly_chart(fig1)

    # --- Graph 2: High Rated Apps vs Low Number of Reviews ---
    top_low_reviewed_apps = unreliable_apps.nlargest(10, 'Rating')
    
    fig2 = px.scatter(
        top_low_reviewed_apps,
        x='App',
        y='Rating',
        size='Reviews',
        color='Rating',
        hover_data={'Installs': True},
        title="High Rated Apps with Low Number of Reviews",
        labels={'App': 'App Name', 'Rating': 'Rating'},
    )
    fig2.update_layout(
        xaxis_title="App Name",
        yaxis_title="Rating",
        xaxis_tickangle=-45,
        template='plotly_white'
    )
    st.plotly_chart(fig2)









    # --- Pie chart showing App Frequency by Category ---
    st.subheader('App Frequency by Category')

    # Aggregate data by Category
    agg_data = apps_df.groupby('Category').agg(
        Frequency=('App', 'count'),
        Avg_Price=('Price', 'mean'),
        Most_Common_Type=('Type', lambda x: x.value_counts().index[0] if x.notnull().any() else 'Unknown')
    ).reset_index()

    # Create an interactive pie chart
    fig = px.pie(
        agg_data, 
        values='Frequency', 
        names='Category', 
        title='App Frequency by Category',
        hover_data=['Frequency']
    )

    # Update the pie chart to show percentages and labels on the slices
    fig.update_traces(textposition='inside', textinfo='percent+label')

    # Display the interactive chart
    st.plotly_chart(fig)


    st.subheader('Top 10 Rated Apps in Google Play Store')

    # 1. Get the top 10 rated apps
    top10_apps = apps_df.sort_values(by='Rating', ascending=False).head(10)

    # 2. Create the interactive bar chart with different colors
    fig = px.bar(
        top10_apps,
        x='App',
        y='Rating',
        hover_data={'Genres': True, 'Installs': True, 'App': False},  # 'App': False to not repeat app name
        title='Top 10 Rated Apps',
        color='App',  # Assigning a unique color to each app
    )

    # 3. Customize layout for better readability
    fig.update_layout(
        title='Top 10 Rated Apps in Google Play Store',  # Main figure title
        xaxis_title='App Name',  # X-axis title
        yaxis_title='Average Rating',  # Y-axis title
        xaxis_tickangle=-45,  # Rotate x-axis labels for better visibility
        template='plotly_white',  # Clean background style
        title_x=0.5,  # Center the title
        title_font=dict(size=20, family='Arial', color='black'),  # Font style for the title
        xaxis_title_font=dict(size=14, family='Arial', color='black'),  # X-axis title font
        yaxis_title_font=dict(size=14, family='Arial', color='black'),  # Y-axis title font
    )

    # 4. Display the interactive chart
    st.plotly_chart(fig)  # Use Streamlit to display the Plotly chart




    # 1. Get the top 10 apps by Installs
    top10_installs = apps_df.sort_values(by='Installs', ascending=False).head(10)

    # 2. Create the interactive bar chart
    fig = px.bar(
        top10_installs,
        x='App',
        y='Installs',
        color='App',  # Different color for each app
        hover_data={'Rating': True, 'Genres': True, 'App': False},  # Hover info: rating and genre
        title='Top 10 Most Installed Apps on Google Play'
    )

    # 3. Customize layout for readability and set label font color to white
    fig.update_layout(
        title='Top 10 Most Installed Apps on Google Play',  # Main figure title
        xaxis_title='App Name',  # X-axis title
        yaxis_title='Installs',  # Y-axis title
        xaxis_tickangle=-45,  # Rotate x-axis labels for better visibility
        template='plotly_white',  # Clean background style
        title_x=0.5,  # Center the title
        title_font=dict(size=20, family='Arial', color='black'),  # Font style for the title
        xaxis_title_font=dict(size=14, family='Arial', color='white'),  # X-axis title font, color white
        yaxis_title_font=dict(size=14, family='Arial', color='white'),  # Y-axis title font, color white
        xaxis_tickfont=dict(size=12, family='Arial', color='white'),  # X-axis labels font, color white
        yaxis_tickfont=dict(size=12, family='Arial', color='white')  # Y-axis labels font, color white
    )

    # 4. Add subheader and display the interactive chart
    st.subheader('Top 10 Most Installed Apps')  # Add a subheader before the chart
    st.plotly_chart(fig)  # Use Streamlit to display the Plotly chart




    # 2. Get the top 10 highest-priced apps
    top10_price = apps_df.sort_values(by='Price', ascending=False).head(10)

    # 3. Create the interactive bar chart
    fig = px.bar(
        top10_price,
        x='App',
        y='Price',
        color='App',  # each bar gets a distinct color
        hover_data={
            'Price': ':.2f',      # show price with two decimal places
            'Genres': True,
            'Installs': True,
            'App': False          # hide the 'App' column in the hover (to avoid repetition)
        },
        title='Top 10 Highest-Priced Apps'
    )

    # 4. Customize the layout with white font color for labels
    fig.update_layout(
        title='Top 10 Highest-Priced Apps',  # Main figure title
        xaxis_title='App Name',  # X-axis title
        yaxis_title='Price (USD)',   # or your currency
        xaxis_tickangle=-45,         # Rotate x-axis labels
        template='plotly_white',     # Clean background style
        title_x=0.5,  # Center the title
        title_font=dict(size=20, family='Arial', color='black'),  # Font style for the title
        xaxis_title_font=dict(size=14, family='Arial', color='white'),  # X-axis title font, color white
        yaxis_title_font=dict(size=14, family='Arial', color='white'),  # Y-axis title font, color white
        xaxis_tickfont=dict(size=12, family='Arial', color='white'),  # X-axis labels font, color white
        yaxis_tickfont=dict(size=12, family='Arial', color='white')  # Y-axis labels font, color white
    )

    # 5. Add subheader and display the interactive chart
    st.subheader('Top 10 Highest-Priced Apps')  # Add a subheader before the chart
    st.plotly_chart(fig)  # Use Streamlit to display the Plotly chart




    # 1. Prepare data
    # Fill any missing 'Type' values to avoid errors
    df_type = apps_df.copy()
    df_type['Type'] = df_type['Type'].fillna('Unknown')

    # Group by Type, counting apps, summing installs, and finding the most common genre
    df_type_grouped = df_type.groupby('Type').agg({
        'App': 'count',
        'Installs': 'sum',
        'Category': lambda x: x.value_counts().index[0] if len(x.value_counts()) > 0 else 'Unknown'
    }).reset_index().rename(columns={'App':'Count','Installs':'TotalInstalls'})

    # Filter to keep only Free/Paid if desired
    df_type_grouped = df_type_grouped[df_type_grouped['Type'].isin(['Free','Paid'])]

    # 2. Create the interactive pie chart
    fig = px.pie(
        df_type_grouped,
        names='Type',
        values='Count',
        hover_data=['TotalInstalls'],  # Shows total installs and top genre on hover
        title='Count of Free vs. Paid Apps'
    )

    # 3. Customize layout for better readability and set font color to white
    fig.update_layout(
        title='Count of Free vs. Paid Apps',  # Main figure title
        xaxis_title='Type',  # X-axis title (although it's a pie chart, you may not need it)
        yaxis_title='Count',  # Y-axis title (again, not as relevant for pie charts)
        template='plotly_white',  # Clean background style
        title_x=0.5,  # Center the title
        title_font=dict(size=20, family='Arial', color='black'),  # Font style for the title
        legend_title_font=dict(size=14, family='Arial', color='white'),  # Font for legend title
    )

    # 4. Add subheader and display the interactive pie chart
    st.subheader('Count of Free vs. Paid Apps')  # Add a subheader before the chart
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',  # Show both percentage and label inside each slice
        textfont=dict(size=12, color='white')  # Make the text color white inside slices
    )

    # 5. Show the chart
    st.plotly_chart(fig)  # Use Streamlit to display the Plotly chart




     # Subheader for Top 10 Paid Apps Most Installed
    st.subheader('Top 10 Most Installed Paid Apps')

    # Filter for paid apps
    paid_apps = apps_df[apps_df['Type'] == 'Paid']

    # Sort by number of installs, descending, and get top 10
    top10_paid_apps = paid_apps.sort_values(by='Installs', ascending=False).head(10)

    # Create a bar chart for top 10 paid apps by install count
    fig = px.bar(
        top10_paid_apps,
        x='App',
        y='Installs',
        color='App',  # Color each bar differently based on the app name
        title='Top 10 Most Installed Paid Apps',
        labels={'App': 'App Name', 'Installs': 'Install Count'},
        hover_data={'Installs': True, 'Price': True},  # Show install count and price on hover
    )

    # Customize layout for better readability
    fig.update_layout(
        xaxis_title='App Name',
        yaxis_title='Install Count',
        xaxis_tickangle=-45,  # Rotate x-axis labels for better visibility
        template='plotly_white'
    )

    # Display the interactive chart
    st.plotly_chart(fig)  # Use Streamlit to display the Plotly chart






    # 1. Group by Genre and sum the installs for each genre
    genre_installs = apps_df.groupby('Genres')['Installs'].sum().reset_index()

    # 2. Sort the genres by installs in descending order and select the top 10
    top10_genres = genre_installs.sort_values(by='Installs', ascending=False).head(10)

    # 3. Create the interactive bar chart
    fig = px.bar(
        top10_genres,
        x='Genres',
        y='Installs',
        color='Genres',  # Color each bar differently
        hover_data={'Genres': True, 'Installs': True},  # Show genre and install count on hover
        title='Top 10 Genres Based on Install Count'
    )

    # 4. Customize layout for better readability and set font color to white
    fig.update_layout(
        title='Top 10 Genres Based on Install Count',  # Main figure title
        xaxis_title='Genre',  # X-axis title
        yaxis_title='Total Installs',  # Y-axis title
        xaxis_tickangle=-45,  # Rotate x-axis labels for better visibility
        template='plotly_white',  # Clean background style
        title_x=0.5,  # Center the title
        title_font=dict(size=20, family='Arial', color='black'),  # Font style for the title
        xaxis_title_font=dict(size=14, family='Arial', color='white'),  # X-axis title font, color white
        yaxis_title_font=dict(size=14, family='Arial', color='white'),  # Y-axis title font, color white
        xaxis_tickfont=dict(size=12, family='Arial', color='white'),  # X-axis labels font, color white
        yaxis_tickfont=dict(size=12, family='Arial', color='white')  # Y-axis labels font, color white
    )

    # 5. Add subheader and display the interactive bar chart
    st.subheader('Top 10 Genres Based on Install Count')  # Add a subheader before the chart
    st.plotly_chart(fig)  # Use Streamlit to display the Plotly chart





    # Subheader for Top 10 Categories by Install Count
    st.subheader('Top 10 Categories by Install Count')

    # Group by 'Category' and sum the installs
    category_installs = apps_df.groupby('Category')['Installs'].sum().reset_index()

    # Sort by installs in descending order and get top 10
    top10_category_installs = category_installs.sort_values(by='Installs', ascending=False).head(10)

    # Create a bar chart for top 10 categories by install count
    fig = px.bar(
        top10_category_installs,
        x='Category',
        y='Installs',
        color='Category',  # Color each category differently
        title='Top 10 Categories by Install Count',
        labels={'Category': 'App Category', 'Installs': 'Install Count'},
        hover_data={'Installs': True},  # Show install count on hover
    )

    # Customize layout for better readability
    fig.update_layout(
        xaxis_title='Category',
        yaxis_title='Install Count',
        xaxis_tickangle=-45,  # Rotate x-axis labels for better visibility
        template='plotly_white'
    )

    # Display the interactive chart
    st.plotly_chart(fig)  # Use Streamlit to display the Plotly chart

























# Time Series Analysis Page
elif page == 'Time Series Analysis':
    st.title('Time Series Analysis of Apps')

    # # Time Series of Size by Category (Top 10 Installed Apps)
    # top10_apps = apps_df.sort_values(by='Installs', ascending=False).head(10)
    # top10_apps_df = apps_df[apps_df['App'].isin(top10_apps['App'])]

    # # Group by App and Last Updated to track the size over time
    # size_time_series = top10_apps_df.groupby(['App', 'Last Updated'])['Size'].mean().reset_index()

    # # Plot the time series of size
    # fig = px.line(
    #     size_time_series,
    #     x='Last Updated',
    #     y='Size',
    #     color='App',
    #     title='Time Series of App Size for Top 10 Most Installed Apps',
    #     labels={'Last Updated': 'Date', 'Size': 'App Size (MB)'},
    #     markers=True
    # )
    # st.plotly_chart(fig)




        # 2. Get the top 3 most installed apps
    top3_installs = apps_df.sort_values(by='Installs', ascending=False).head(50)

    # 3. Filter the main dataset to include only the top 3 apps
    top3_apps_df = apps_df[apps_df['App'].isin(top3_installs['App'])]

    # 4. Group by App and Last Updated, summing the installs
    time_series_df = top3_apps_df.groupby(['App', 'Last Updated'])['Installs'].sum().reset_index()

    # 5. Create the interactive time series plot
    fig = px.line(
        time_series_df,
        x='Last Updated',
        y='Installs',
        color='App',  # Different colors for each app
        title='Install Count Over Time for Top 50 Most Installed Apps',
        labels={'Last Updated': 'Date', 'Installs': 'Install Count'},
        markers=True  # Show markers on the line plot for each data point
    )

    # 6. Update hover data to show app name and precise update date
    fig.update_traces(
        hovertemplate="<b>App:</b> %{customdata[0]}<br>" +  # App name
                    "<b>Date:</b> %{x}<br>" +               # Precise update date
                    "<b>Installs:</b> %{y}<br>",            # Install count
        customdata=time_series_df[['App']].values  # Custom data for the app name
    )

    # 7. Customize layout with white font color for labels
    fig.update_layout(
        title='Install Count Over Time for Top 3 Most Installed Apps',  # Main figure title
        xaxis_title='Date',  # X-axis title
        yaxis_title='Install Count',  # Y-axis title
        template='plotly_white',  # Clean background style
        title_x=0.5,  # Center the title
        title_font=dict(size=20, family='Arial', color='black'),  # Font style for the title
        xaxis_title_font=dict(size=14, family='Arial', color='white'),  # X-axis title font, color white
        yaxis_title_font=dict(size=14, family='Arial', color='white'),  # Y-axis title font, color white
        xaxis_tickfont=dict(size=12, family='Arial', color='white'),  # X-axis labels font, color white
        yaxis_tickfont=dict(size=12, family='Arial', color='white')  # Y-axis labels font, color white
    )

    # 8. Add subheader and display the interactive time series plot
    st.subheader('Install Count Over Time for Top 50 Most Installed Apps')  # Add a subheader before the chart
    st.plotly_chart(fig)  # Use Streamlit to display the Plotly chart






    # 1. Group the apps by Genre and sum the installs for each genre
    genre_installs = apps_df.groupby('Genres')['Installs'].sum().reset_index()

    # 2. Sort the genres by total installs in descending order
    sorted_genres = genre_installs.sort_values(by='Installs', ascending=False)

    # 3. Create an interactive bar chart to show installs per genre
    fig = px.bar(
        sorted_genres,
        x='Genres',
        y='Installs',
        color='Genres',  # Color each genre differently
        title='Total Install Count by Genre',
        labels={'Genres': 'App Genre', 'Installs': 'Total Installs'},
        hover_data={'Genres': True, 'Installs': True},  # Show genre and total installs on hover
    )

    # 4. Customize layout for better readability and set font color to white
    fig.update_layout(
        title='Total Install Count by Genre',  # Main figure title
        xaxis_title='Genre',  # X-axis title
        yaxis_title='Total Installs',  # Y-axis title
        xaxis_tickangle=-45,  # Rotate x-axis labels for better visibility
        template='plotly_white',  # Clean background style
        title_x=0.5,  # Center the title
        title_font=dict(size=20, family='Arial', color='black'),  # Font style for the title
        xaxis_title_font=dict(size=14, family='Arial', color='white'),  # X-axis title font, color white
        yaxis_title_font=dict(size=14, family='Arial', color='white'),  # Y-axis title font, color white
        xaxis_tickfont=dict(size=12, family='Arial', color='white'),  # X-axis labels font, color white
        yaxis_tickfont=dict(size=12, family='Arial', color='white')  # Y-axis labels font, color white
    )

    # 5. Add subheader and display the interactive bar chart
    st.subheader('Total Install Count by Genre')  # Add a subheader before the chart
    st.plotly_chart(fig)  # Use Streamlit to display the Plotly chart






    # 1. Ensure 'Last Updated' is in datetime format
    apps_df['Last Updated'] = pd.to_datetime(apps_df['Last Updated'], errors='coerce')

    # 2. Group by Category and Last Updated, calculating the average rating for each date
    category_rating_time_series = apps_df.groupby(['Category', 'Last Updated'])['Rating'].mean().reset_index()

    # 3. Create the time series plot for each category
    fig = px.line(
        category_rating_time_series,
        x='Last Updated',
        y='Rating',
        color='Category',  # Different colors for each category
        title='Time Series of App Ratings by Category',
        labels={'Last Updated': 'Date', 'Rating': 'Average Rating'},
        markers=True  # Show markers on the line plot for each data point
    )

    # 4. Customize layout for better readability and set font color to white
    fig.update_layout(
        title='Time Series of App Ratings by Category',  # Main figure title
        xaxis_title='Date',  # X-axis title
        yaxis_title='Average Rating',  # Y-axis title
        template='plotly_white',  # Clean background style
        title_x=0.5,  # Center the title
        title_font=dict(size=20, family='Arial', color='black'),  # Font style for the title
        xaxis_title_font=dict(size=14, family='Arial', color='white'),  # X-axis title font, color white
        yaxis_title_font=dict(size=14, family='Arial', color='white'),  # Y-axis title font, color white
        xaxis_tickfont=dict(size=12, family='Arial', color='white'),  # X-axis labels font, color white
        yaxis_tickfont=dict(size=12, family='Arial', color='white')  # Y-axis labels font, color white
    )

    # 5. Add subheader and display the interactive time series plot
    st.subheader('Time Series of App Ratings by Category')  # Add a subheader before the chart
    st.plotly_chart(fig)  # Use Streamlit to display the Plotly chart






    # 1. Ensure 'Last Updated' is in datetime format
    apps_df['Last Updated'] = pd.to_datetime(apps_df['Last Updated'], errors='coerce')

    # 2. Group by 'Category' and 'Last Updated', summing installs
    category_installs_time_series = apps_df.groupby(['Category', 'Last Updated'])['Installs'].sum().reset_index()

    # 3. Create the time series plot for each category
    fig = px.line(
        category_installs_time_series,
        x='Last Updated',
        y='Installs',
        color='Category',  # Different colors for each category
        title='Time Series of Total Installs by Category',
        labels={'Last Updated': 'Date', 'Installs': 'Total Installs'},
        markers=True  # Show markers on the line plot for each data point
    )

    # 4. Customize layout for better readability and set font color to white
    fig.update_layout(
        title='Time Series of Total Installs by Category',  # Main figure title
        xaxis_title='Date',  # X-axis title
        yaxis_title='Total Installs',  # Y-axis title
        template='plotly_white',  # Clean background style
        title_x=0.5,  # Center the title
        title_font=dict(size=20, family='Arial', color='black'),  # Font style for the title
        xaxis_title_font=dict(size=14, family='Arial', color='white'),  # X-axis title font, color white
        yaxis_title_font=dict(size=14, family='Arial', color='white'),  # Y-axis title font, color white
        xaxis_tickfont=dict(size=12, family='Arial', color='white'),  # X-axis labels font, color white
        yaxis_tickfont=dict(size=12, family='Arial', color='white')  # Y-axis labels font, color white
    )

    # 5. Add subheader and display the interactive time series plot
    st.subheader('Time Series of Total Installs by Category')  # Add a subheader before the chart
    st.plotly_chart(fig)  # Use Streamlit to display the Plotly chart






    # 1. Ensure 'Last Updated' is in datetime format
    apps_df['Last Updated'] = pd.to_datetime(apps_df['Last Updated'], errors='coerce')

    # 2. Ensure 'Size' is numeric (since size might include 'M' or 'K', we need to clean it)
    def parse_size(size):
        if isinstance(size, str):
            size = size.lower().replace('m', '').replace('k', '').strip()
            try:
                size = float(size)
            except ValueError:
                return None
        return size

    apps_df['Size'] = apps_df['Size'].apply(parse_size)

    # 3. Get the top 10 most installed apps
    top10_installs = apps_df.sort_values(by='Installs', ascending=False).head(700)

    # 4. Filter the data for the top 10 most installed apps
    top10_apps_df = apps_df[apps_df['App'].isin(top10_installs['App'])]

    # 5. Group by 'App' and 'Last Updated', taking the size for each app at each update
    size_time_series = top10_apps_df.groupby(['App', 'Last Updated'])['Size'].mean().reset_index()

    # 6. Create the time series plot for the size of the top 10 apps
    fig = px.line(
        size_time_series,
        x='Last Updated',
        y='Size',
        color='App',  # Different colors for each app
        title='Time Series of App Size for Top 10 Most Installed Apps',
        labels={'Last Updated': 'Date', 'Size': 'App Size (MB)'},
        markers=True  # Show markers on the line plot for each data point
    )

    # 7. Customize layout for better readability and set font color to white
    fig.update_layout(
        title='Time Series of App Size for Top 10 Most Installed Apps',  # Main figure title
        xaxis_title='Date',  # X-axis title
        yaxis_title='App Size (MB)',  # Y-axis title
        template='plotly_white',  # Clean background style
        title_x=0.5,  # Center the title
        title_font=dict(size=20, family='Arial', color='black'),  # Font style for the title
        xaxis_title_font=dict(size=14, family='Arial', color='white'),  # X-axis title font, color white
        yaxis_title_font=dict(size=14, family='Arial', color='white'),  # Y-axis title font, color white
        xaxis_tickfont=dict(size=12, family='Arial', color='white'),  # X-axis labels font, color white
        yaxis_tickfont=dict(size=12, family='Arial', color='white')  # Y-axis labels font, color white
    )

    # 8. Add subheader and display the interactive time series plot
    st.subheader('Time Series of App Size for Most Installed Apps')  # Add a subheader before the chart
    st.plotly_chart(fig)  # Use Streamlit to display the Plotly chart








          

























# Game Page
if page == 'Game':
    st.title('Game Category Analysis')

    # Subheader for the Top 10 Game Apps by Install Count
    st.subheader('Top Apps in Game Category by Install Count')

    # Filter for Game category apps
    game_apps = apps_df[apps_df['Category'] == 'GAME']

    # Sort by install count and get the top 10 game apps
    top10_game_apps = game_apps.sort_values(by='Installs', ascending=False).head(10)

    # Create a bar chart for top 10 game apps by install count
    fig1 = px.bar(
        top10_game_apps,
        x='App',
        y='Installs',
        color='App',  # Color each app differently
        title='Top Apps in Game Category by Install Count',
        labels={'App': 'App Name', 'Installs': 'Install Count'},
        hover_data={'Installs': True},  # Show install count on hover
    )
    
    # Customize the layout
    fig1.update_layout(
        xaxis_title="App Name",
        yaxis_title="Install Count",
        xaxis_tickangle=-45,
        template='plotly_white'
    )

    # Display the first graph
    st.plotly_chart(fig1)

    # Insights for Top 10 Apps in Game Category
    st.write("""
        **Insight**: The top 10 most installed game apps showcase which games are the most popular among users. 
        These apps typically have high visibility and engagement, which contributes to their large install base. 
        The install count serves as a reliable indicator of user preference, although it is important to consider other factors like ratings and reviews to get a better understanding of app quality.
    """)

    # Subheader for Highest Number of Reviews vs Install Count in Game Category
    st.subheader('Highest Number of Reviews vs Install Count in Game Category')

    # Sort by the number of reviews and select top game apps
    top_reviews_game_apps = game_apps.sort_values(by='Reviews', ascending=False).head(10)

    # Create a scatter plot for reviews vs install count
    fig2 = px.scatter(
        top_reviews_game_apps,
        x='Reviews',
        y='Installs',
        size='Reviews',
        color='App',  # Color each app differently
        title='Highest Number of Reviews vs Install Count for Game Category',
        labels={'Reviews': 'Number of Reviews', 'Installs': 'Install Count'},
        hover_data={'App': True, 'Reviews': True, 'Installs': True},  # Show app name, reviews, and installs on hover
    )

    # Customize the layout
    fig2.update_layout(
        xaxis_title="Number of Reviews",
        yaxis_title="Install Count",
        template='plotly_white'
    )

    # Display the second graph
    st.plotly_chart(fig2)

    # Insights for Highest Number of Reviews vs Install Count
    st.write("""
        **Insight**: The second graph shows the relationship between install count and number of reviews for game apps. 
        Games with a higher number of reviews generally have larger user bases, which is often an indicator of a popular or well-established app. 
        However, high install counts with lower review numbers might indicate a more recent app or a game with a more limited audience. 
        The review count helps assess the app's trustworthiness and user feedback.
    """)




























# Communication Page
if page == 'Communication':
    st.title('Communication Category Analysis')
    

    # Filter for Communication category apps
    communication_apps = apps_df[apps_df['Category'] == 'COMMUNICATION']
    
    # Check if the Communication category contains any data
    if communication_apps.empty:
        st.write("No data available for the Communication category.")
    else:
        # Clean the Installs column to ensure it is numeric
        communication_apps['Installs'] = communication_apps['Installs'].replace('[\+,]', '', regex=True)  # Remove '+' and ','
        communication_apps['Installs'] = pd.to_numeric(communication_apps['Installs'], errors='coerce')  # Convert to numeric, invalid parsing results in NaN
        communication_apps['Reviews'] = pd.to_numeric(communication_apps['Reviews'], errors='coerce')  # Convert Reviews to numeric

        # Drop NaN values from 'Installs' for safe calculations
        communication_apps = communication_apps.dropna(subset=['Installs'])

        # --- Find the most installed app in the Communication category ---
        most_installed_app = communication_apps.loc[communication_apps['Installs'].idxmax()]

        # Show the most installed app
        st.subheader(f"Most Installed App in Communication Category")
        # st.write(f"Install Count: {most_installed_app['Installs']}")
        # st.write(f"Rating: {most_installed_app['Rating']}")
        
        # --- Find the top 10 most installed apps in the Communication category ---
        top10_installed_communication_apps = communication_apps.sort_values(by='Installs', ascending=False).head(10)

        # Create a bar chart for the top 10 most installed apps in the Communication category
        fig1 = px.bar(
            top10_installed_communication_apps,
            x='App',
            y='Installs',
            color='App',  # Color each app differently
            title='Top Most Installed Apps in Communication Category',
            labels={'App': 'App Name', 'Installs': 'Install Count'},
            hover_data={'Installs': True},  # Show install count on hover
        )
        fig1.update_layout(
            xaxis_title="App Name",
            yaxis_title="Install Count",
            xaxis_tickangle=-45,
            template='plotly_white'
        )
        st.plotly_chart(fig1)

        # --- Create the scatter plot for most reviewed apps vs rating ---
        top10_reviewed_apps = communication_apps.sort_values(by='Reviews', ascending=False).head(10)

        # Create a scatter plot for most reviewed apps vs rating
        fig2 = px.scatter(
            top10_reviewed_apps,
            x='Reviews',
            y='Rating',
            size='Reviews',
            color='App',  # Color each app differently
            title='Top Most Reviewed Apps vs Rating in Communication Category',
            labels={'Reviews': 'Number of Reviews', 'Rating': 'App Rating'},
            hover_data={'App': True, 'Reviews': True, 'Rating': True},  # Show app name, reviews, and rating on hover
        )
        fig2.update_layout(
            xaxis_title="Number of Reviews",
            yaxis_title="Rating",
            template='plotly_white'
        )
        st.plotly_chart(fig2)

        # Insights
        st.write("""
            **Insight**: The first graph shows the top most installed apps in the Communication category. Apps with higher install counts typically indicate a larger user base, which often translates to higher trust and reliability.
            The second graph shows the relationship between the **number of reviews** and **app rating**. Apps with higher reviews generally have a larger user base, and the ratings give an indication of how well the app is received.
        """)





















# Social Page
if page == 'Social':
    st.title('Social Category Analysis')


    # Filter for Social category apps
    social_apps = apps_df[apps_df['Category'] == 'SOCIAL']
    
    # Check if the Social category contains any data
    if social_apps.empty:
        st.write("No data available for the Social category.")
    else:
        # Clean the Installs and Reviews columns to ensure they are numeric
        social_apps['Installs'] = social_apps['Installs'].replace('[\+,]', '', regex=True)  # Remove '+' and ','
        social_apps['Installs'] = pd.to_numeric(social_apps['Installs'], errors='coerce')  # Convert to numeric, invalid parsing results in NaN
        social_apps['Reviews'] = pd.to_numeric(social_apps['Reviews'], errors='coerce')  # Convert Reviews to numeric

        # Drop NaN values from 'Installs' for safe calculations
        social_apps = social_apps.dropna(subset=['Installs'])

        # --- Find the most installed app in the Social category ---
        most_installed_app = social_apps.loc[social_apps['Installs'].idxmax()]

        # Show the most installed app
        st.subheader(f"Most Installed App in Social Category")
        # st.write(f"Install Count: {most_installed_app['Installs']}")
        # st.write(f"Rating: {most_installed_app['Rating']}")
        
        # --- Find the top 10 most installed apps in the Social category ---
        top10_installed_social_apps = social_apps.sort_values(by='Installs', ascending=False).head(10)

        # Create a bar chart for the top 10 most installed apps in the Social category
        fig1 = px.bar(
            top10_installed_social_apps,
            x='App',
            y='Installs',
            color='App',  # Color each app differently
            title='Top Most Installed Apps in Social Category',
            labels={'App': 'App Name', 'Installs': 'Install Count'},
            hover_data={'Installs': True},  # Show install count on hover
        )
        fig1.update_layout(
            xaxis_title="App Name",
            yaxis_title="Install Count",
            xaxis_tickangle=-45,
            template='plotly_white'
        )
        st.plotly_chart(fig1)

        # --- Create the scatter plot for most reviewed apps vs rating ---
        top10_reviewed_apps_social = social_apps.sort_values(by='Reviews', ascending=False).head(10)

        # Create a scatter plot for most reviewed apps vs rating
        fig2 = px.scatter(
            top10_reviewed_apps_social,
            x='Reviews',
            y='Rating',
            size='Reviews',
            color='App',  # Color each app differently
            title='Top Most Reviewed Apps vs Rating in Social Category',
            labels={'Reviews': 'Number of Reviews', 'Rating': 'App Rating'},
            hover_data={'App': True, 'Reviews': True, 'Rating': True},  # Show app name, reviews, and rating on hover
        )
        fig2.update_layout(
            xaxis_title="Number of Reviews",
            yaxis_title="Rating",
            template='plotly_white'
        )
        st.plotly_chart(fig2)

        # # Insights
        # st.write("""
        #     **Insight**: The first graph shows the top most installed apps in the Social category. Apps with higher install counts typically indicate a larger user base, which often translates to higher trust and reliability.
        #     The second graph shows the relationship between the **number of reviews** and **app rating**. Apps with higher reviews generally have a larger user base, and the ratings give an indication of how well the app is received.
        # """)
