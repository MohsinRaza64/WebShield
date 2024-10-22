import threading
from proxy.proxy_server import start_proxy 
from malware_detector.file_processor import start_file_processor
from gui.dashboard_extended import Dashboard

def run_proxy():
    start_proxy()

def run_file_processor():
    start_file_processor()

if __name__ == "__main__":

    proxy_thread = threading.Thread(target=run_proxy)
    proxy_thread.start()
    
    file_processor_thread = threading.Thread(target=run_file_processor)
    file_processor_thread.start()
    print("Starting")
    app = Dashboard()
    app.run()

    proxy_thread.join()
    file_processor_thread.join()