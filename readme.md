
# ArcGIS + Gemini AI Search App

This Streamlit application combines ArcGIS search capabilities with Google's Gemini AI to provide intelligent analysis of GIS resources.

## Features

- Search for GIS resources using ArcGIS
- AI-enhanced analysis of search results
- Suggestions for resource usage
- Recommendations for better search terms

## Setup Instructions

1. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

2. Get a Google Gemini API key from: https://aistudio.google.com/app/apikey

3. Run the Streamlit app:
   ```
   streamlit run app.py
   ```

4. Enter your API key in the sidebar when the app launches

## Usage

1. Enter a search term (e.g., "california wildfires")
2. Select the item type (Feature Service, Map Service, Web Map, or Any)
3. Set the maximum number of results
4. Click "Search"
5. Review the raw results and AI analysis

## Notes

- The app implements rate limiting and exponential backoff for API calls
- If the AI analysis fails, a basic fallback analysis is provided
