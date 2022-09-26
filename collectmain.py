import atexit

from browser.manager import init_manager as init_browser_manager
from output.manager import OutputManager
from proxy.manager import init_manager as init_proxy_manager

def DyCollectService(tableSingal,rootUrl):
    global proxy_manager
    global browser_manager
    global output_manager

    proxy_manager = init_proxy_manager()
    proxy_manager.start_loop()
    browser_manager = init_browser_manager(rootUrl)
    output_manager = OutputManager(tableSingal)

    atexit.register(terminate)

    output_manager.start_loop()
    try:
        proxy_manager.join()
    finally:
        terminate()

def terminate(*_):
    print("terminate")
    browser_manager.terminate()
    output_manager.terminate()
    proxy_manager.terminate()
