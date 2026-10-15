"""
Bank Data Visualizer - Desktop Launcher
Starts the Streamlit app in standalone mode
"""

import sys
import os
import subprocess
import time
import webbrowser
from pathlib import Path
import socket

def find_free_port():
    """Find a free port to run Streamlit on"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port

def main():
    # Get the directory where the script is located
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        app_dir = Path(sys._MEIPASS)
    else:
        # Running as script
        app_dir = Path(__file__).parent
    
    # Find a free port
    port = find_free_port()
    
    # Set environment variables
    os.environ['STREAMLIT_SERVER_PORT'] = str(port)
    os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
    os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
    
    # Path to the Streamlit app
    app_path = app_dir / 'src' / 'app.py'
    
    # Start Streamlit as subprocess
    streamlit_cmd = [
        sys.executable,
        '-m', 'streamlit',
        'run',
        str(app_path),
        '--server.port', str(port),
        '--server.headless', 'true',
        '--browser.gatherUsageStats', 'false',
        '--server.fileWatcherType', 'none'
    ]
    
    # Start Streamlit
    process = subprocess.Popen(
        streamlit_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
    )
    
    # Wait a bit for Streamlit to start
    time.sleep(3)
    
    # Open browser
    url = f'http://localhost:{port}'
    webbrowser.open(url)
    
    print(f"Bank Data Visualizer started at {url}")
    print("Close this window to stop the application.")
    
    try:
        # Wait for process to finish
        process.wait()
    except KeyboardInterrupt:
        process.terminate()
        print("\nApplication stopped.")

if __name__ == '__main__':
    main()
