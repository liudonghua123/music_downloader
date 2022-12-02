
# some help functions
from dataclasses import dataclass
import sys
from os.path import dirname, join, realpath
from playwright.sync_api._generated import Page

#%%
# In order to run this script directly, you need to add the parent directory to the sys.path
# Or you need to run this script in the parent directory using the command: python -m client.algorithm
sys.path.append(dirname(realpath(__file__)))
from common.config_logging import init_logging

logger = init_logging(join(dirname(realpath(__file__)), "main.log"))

def selector_exists(element, selector):
    exists = False
    locator = None
    try:
        locator = element.locator(selector)
        exists = True
    except:
        exists = False
    return exists, locator

def focus_and_click(page: Page, selector: str):
    result = True
    try:
        page.focus(selector)
        page.click(selector)
    except:
        logger.error(f"failed to focus_and_click {selector}")
        result = False
    return result