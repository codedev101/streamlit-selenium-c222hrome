import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
from bs4 import BeautifulSoup
import time

st.title("Web Scraper with Selenium")
st.markdown("[![Source](https://img.shields.io/badge/View-Source-blue.svg)](https://github.com/snehankekre/streamlit-selenium-chrome/)")

@st.cache_resource
def get_driver():
    """Initialize Chrome driver with proper options for Streamlit Cloud"""
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-web-security")
    
    try:
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()),
            options=options,
        )
        return driver
    except Exception as e:
        st.error(f"Failed to initialize Chrome driver: {e}")
        return None

def scrape_website(url, driver):
    """Scrape website content and return parsed data"""
    try:
        st.info(f"Loading {url}...")
        driver.get(url)
        time.sleep(2)  # Wait for page to load
        
        # Get page source
        page_source = driver.page_source
        
        # Parse with BeautifulSoup for better content extraction
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Extract meaningful content
        title = soup.find('title')
        title_text = title.get_text().strip() if title else "No title found"
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text content
        text_content = soup.get_text()
        
        # Clean up text (remove extra whitespace)
        lines = (line.strip() for line in text_content.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        clean_text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return {
            'title': title_text,
            'raw_html': page_source,
            'clean_text': clean_text,
            'status': 'success'
        }
        
    except Exception as e:
        return {
            'title': '',
            'raw_html': '',
            'clean_text': '',
            'status': f'error: {str(e)}'
        }

# Main UI
url_input = st.text_input(
    "Enter URL to scrape:", 
    value="http://example.com",
    placeholder="https://example.com"
)

if st.button("Scrape Website", type="primary"):
    if url_input:
        # Initialize driver
        driver = get_driver()
        
        if driver:
            try:
                # Scrape the website
                result = scrape_website(url_input, driver)
                
                if result['status'] == 'success':
                    st.success("Scraping completed successfully!")
                    
                    # Display results in tabs
                    tab1, tab2, tab3 = st.tabs(["Page Content", "Raw HTML", "Page Title"])
                    
                    with tab1:
                        st.subheader("Extracted Text Content")
                        if result['clean_text']:
                            st.text_area(
                                "Clean Text Content:", 
                                value=result['clean_text'][:5000] + ("..." if len(result['clean_text']) > 5000 else ""),
                                height=400,
                                disabled=True
                            )
                        else:
                            st.warning("No text content found on the page.")
                    
                    with tab2:
                        st.subheader("Raw HTML Source")
                        st.code(result['raw_html'][:3000] + ("..." if len(result['raw_html']) > 3000 else ""), language='html')
                    
                    with tab3:
                        st.subheader("Page Information")
                        st.write(f"**Title:** {result['title']}")
                        st.write(f"**URL:** {url_input}")
                        st.write(f"**Content Length:** {len(result['clean_text'])} characters")
                        st.write(f"**HTML Length:** {len(result['raw_html'])} characters")
                
                else:
                    st.error(f"Scraping failed: {result['status']}")
                    
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
            
            finally:
                # Clean up driver
                try:
                    driver.quit()
                except:
                    pass
        else:
            st.error("Failed to initialize web driver. Please try again.")
    else:
        st.warning("Please enter a valid URL.")

# Additional information
with st.expander("ℹ️ How this works"):
    st.markdown("""
    This app uses Selenium with Chrome to scrape web content:
    
    1. **Chrome Driver Setup**: Automatically downloads and configures ChromeDriver
    2. **Headless Browsing**: Runs Chrome in headless mode (no GUI)
    3. **Content Extraction**: Uses BeautifulSoup to parse and clean HTML content
    4. **Multiple Views**: Shows both clean text and raw HTML
    
    **Features:**
    - Works on Streamlit Cloud with proper Chrome configuration
    - Handles JavaScript-rendered content (unlike simple requests)
    - Extracts clean, readable text from web pages
    - Shows page title and content statistics
    
    **Note:** Some websites may block automated scraping or require additional handling for complex JavaScript.
    """)

# Troubleshooting section
with st.expander("🔧 Troubleshooting"):
    st.markdown("""
    **Common Issues:**
    
    1. **Permission Denied Errors**: This setup should work on Streamlit Cloud with proper Chrome options
    2. **Slow Loading**: Some pages take time to load; the app waits 2 seconds after page load
    3. **Empty Content**: Some sites use heavy JavaScript that may not render in time
    4. **Blocked Access**: Some websites block automated browsers
    
    **Solutions:**
    - Try different URLs if one doesn't work
    - For complex sites, you might need longer wait times
    - Some sites require cookies or headers to access content
    """)
