# -*- coding: utf-8 -*-
{
    "name": "Popup notifications",
    "author": "Divya Vyas",
    "application": True,
    "installable": True,
    "auto_install": False,
    "depends": [
        "base","sale","purchase"
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/popup_notifications.xml"
    ],
    "qweb": [
        "static/xml/base_popup.xml"
    ],
    "external_dependencies": {},
    "summary": "Use popup notification to develop your modules",
    "description": """
""",
    "images": [
        "static/description/main.png"
    ],
}
