import streamlit as st
from arcgis.gis import GIS
import google.generativeai as genai
import time
import random
import os

# Page configuration
st.set_page_config(
    page_title="ArcGIS + Gemini AI Search",
    page_icon="🌎",
    layout="wide"
)

# App title and description
st.title("🌎 ArcGIS + Gemini AI Search")
st.markdown("Search for GIS resources with AI-enhanced analysis")

# Sidebar for API key input
with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("Enter your Google Gemini API key", type="password")
    st.caption("Get an API key from: https://aistudio.google.com/app/apikey")
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown("This app combines ArcGIS search with Google's Gemini AI to provide intelligent analysis of GIS resources.")

# Main function
def main():
    # Connect to ArcGIS
    gis = GIS()
    
    # Configure Gemini if API key is provided
    if api_key:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        # Search parameters
        col1, col2 = st.columns(2)
        with col1:
            query = st.text_input("Enter search term", placeholder="e.g., california wildfires")
        
        with col2:
            item_types = ["Feature Service", "Map Service", "Web Map", "Any"]
            selected_type = st.selectbox("Select item type", item_types)
            # Convert "Any" to None for the API
            item_type_param = None if selected_type == "Any" else selected_type
        
        max_items = st.slider("Maximum number of results", min_value=1, max_value=20, value=5)
        
        # Search button
        if st.button("Search", type="primary"):
            if query:
                with st.spinner(f"Searching for '{query}' with type '{selected_type}', max {max_items} results..."):
                    results = intelligent_geo_search(gis, model, query, item_type_param, max_items)
                    display_results(results)
            else:
                st.warning("Please enter a search term")
    else:
        st.warning("Please enter your Google Gemini API key in the sidebar to use this app")
        st.info("Don't have an API key? Get one from: https://aistudio.google.com/app/apikey")

# Function to perform intelligent search with rate limiting
def intelligent_geo_search(gis, model, query, item_type="Feature Service", max_items=5, retry_attempts=3):
    # 1. Search ArcGIS for content
    search_results = gis.content.search(
        query=query,
        item_type=item_type,
        max_items=max_items
    )

    # 2. Extract relevant information from results
    results_info = []
    for item in search_results:
        results_info.append({
            "title": item.title,
            "type": item.type,
            "description": item.description if hasattr(item, 'description') else "No description available",
            "url": item.url if hasattr(item, 'url') else "No URL available"
        })

    # 3. Use Gemini to analyze and enhance the results with rate limiting and retries
    ai_analysis = "AI analysis not available."

    if results_info:
        prompt = f'''
        I found these GIS resources related to "{query}":
        {results_info}

        Please analyze these results and provide:
        1. A summary of the most relevant resources
        2. Suggestions for how these resources could be used
        3. Additional search terms that might yield better results
        '''

        # Implement rate limiting with exponential backoff
        for attempt in range(retry_attempts):
            try:
                # Add a delay before API call - exponential backoff
                delay = (2 ** attempt) + random.random()
                status_text = st.empty()
                status_text.info(f"Waiting {delay:.2f} seconds before AI analysis (attempt {attempt+1}/{retry_attempts})...")
                time.sleep(delay)

                # Make the API call
                response = model.generate_content(prompt)
                ai_analysis = response.text
                status_text.success("AI analysis successful!")
                break  # Exit the retry loop if successful

            except Exception as e:
                status_text.error(f"Error with AI analysis (attempt {attempt+1}/{retry_attempts}): {str(e)}")
                if attempt == retry_attempts - 1:
                    # Last attempt failed, provide basic analysis
                    ai_analysis = f"Found {len(results_info)} results related to '{query}'.\n\nPossible uses:\n- Visualization of {query} data\n- Analysis of spatial patterns\n- Integration with other datasets"
                    status_text.info("Using fallback analysis.")

        return {
            "raw_results": results_info,
            "ai_analysis": ai_analysis
        }
    else:
        return {"message": "No results found"}

# Function to display results in a more readable format
def display_results(results):
    if "message" in results:
        st.info(results["message"])
        return

    # Display raw results in an expander
    with st.expander("Raw GIS Results", expanded=True):
        for i, item in enumerate(results["raw_results"]):
            st.subheader(f"{i+1}. {item['title']}")
            st.caption(f"Type: {item['type']}")
            
            # Make URL clickable
            if item['url'] != "No URL available":
                st.markdown(f"[Open in ArcGIS]({item['url']})")
            else:
                st.text("No URL available")
            
            st.divider()

    # Display AI analysis
    st.header("AI Analysis")
    st.markdown(results.get("ai_analysis", "No analysis available"))

if __name__ == "__main__":
    main()
