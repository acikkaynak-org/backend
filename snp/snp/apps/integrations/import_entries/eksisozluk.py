from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .base import BaseImportAdapter


class EksiImportAdapter(BaseImportAdapter):
    BASE_URL = "http://eksisozluk.com/"

    @classmethod
    def _parse_single_topic_item(cls, user, topic_item):
        title_text = topic_item.find_element_by_id("title").find_elements_by_tag_name("span")[0].text
        entry_content = topic_item.find_element_by_class_name("content").get_attribute("innerHTML")
        return {
            'title__name': title_text,
            'author': user,
            'content': cls._transform_entry(entry_content),
        }

    @staticmethod
    def _open_all_pages(driver):
        while True:
            try:
                WebDriverWait(driver, 5, 0.25).until(
                    EC.visibility_of_element_located([By.CLASS_NAME, 'load-more-entries'])
                ).click()
            except WebDriverException:
                break

    @staticmethod
    def _transform_entry(entry_content):
        """
        Transform entries from eksisozluk.com to aciksozluk.com entries.
        Various links and references are all turned into aciksozluk.org if desired
        """
        return entry_content

    @classmethod
    def get_entries(cls, user, username):
        driver = cls._get_driver()
        driver.get(f"http://eksisozluk.com/biri/{username}/")
        cls._open_all_pages(driver)
        for topic_item in driver.find_elements_by_class_name("topic-item"):
            yield cls._parse_single_topic_item(user, topic_item)

    @classmethod
    def _sync_backup_xml(cls, backup):
        ...
