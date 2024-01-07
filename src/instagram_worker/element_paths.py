import json
import os


class XPaths:
    def __get_xpaths() -> dict:
        xpaths_file_path = os.path.join(os.getcwd(), "data", "xpaths.json")
        if not os.path.exists(xpaths_file_path):
            raise Exception("No xpaths.json file found")
        with open(xpaths_file_path) as f:
            return json.load(f)

    __xpaths = __get_xpaths()

    @classmethod
    def get_xpath(cls, name: str) -> str | None:
        return cls.__xpaths.get(name)


class CSSClasses:
    def __get_css_classes() -> dict:
        xpaths_file_path = os.path.join(os.getcwd(), "data", "css_classes.json")
        if not os.path.exists(xpaths_file_path):
            raise Exception("No xpaths.json file found")
        with open(xpaths_file_path) as f:
            return json.load(f)

    __css_classes = __get_css_classes()

    @classmethod
    def get_css_class(cls, name: str) -> str | None:
        return cls.__css_classes.get(name)
