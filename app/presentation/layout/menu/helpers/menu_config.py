MENU_OPTIONS = [
    {"name": "dashboard", "roles": ["regular", "admin"]},
    {"name": "explore", "roles": ["regular", "admin"]},
    {"name": "manage", "roles": ["admin"]},
    {"name": "notifications", "roles": ["regular", "admin"]},
    {"name": "profile", "roles": ["regular", "admin"]},
    {"name": "settings", "roles": ["regular", "admin"]},
    {"name": "signOut", "roles": ["regular", "admin"]},
]

# Image paths mapping: {button_name: {state: path}}
# State: "default" (light background), "selected" (dark background / hover state)
MENU_IMAGES_PATHS = {
    "dashboard": {
        "default": "app/assets/images/home/menu/DashboardDefault.png",
        "selected": "app/assets/images/home/menu/dashboardSelect.png",
    },
    "explore": {
        "default": "app/assets/images/home/menu/ExploreDefault.png",
        "selected": "app/assets/images/home/menu/exploreSelect.png",
    },
    "manage": {
        "default": "app/assets/images/home/menu/ManageDefault.png",
        "selected": "app/assets/images/home/menu/manageSelect.png",
    },
    "notifications": {
        "default": "app/assets/images/home/menu/NotificationsDefault.png",
        "selected": "app/assets/images/home/menu/notificationsSelect.png",
    },
    "profile": {
        "default": "app/assets/images/home/menu/ProfileDefault.png",
        "selected": "app/assets/images/home/menu/profileSelect.png",
    },
    "settings": {
        "default": "app/assets/images/home/menu/SettingsDefault.png",
        "selected": "app/assets/images/home/menu/settingsSelect.png",
    },
    "signOut": {
        "default": "app/assets/images/home/menu/signOutDefault.png",
        "selected": "app/assets/images/home/menu/signOutSelect.png",
    },
}

# Menu layout positioning
MENU_LAYOUT = {
    "gap": 50,
    "admin_start_x": 130,
    "regular_start_x": 211,  # Centered: (1350 - (6*113 + 5*50)) / 2
    "menu_y": 310,
}
