MENU_OPTIONS = [
    {"name": "explore", "roles": ["regular", "admin"]},
    {"name": "profile", "roles": ["regular", "admin"]},
    {"name": "notifications", "roles": ["regular", "admin"]},
    {"name": "manage", "roles": ["admin"]},
    {"name": "signOut", "roles": ["regular", "admin"]},
]

# Image paths mapping: {button_name: {state: path}}
# State: "default" (light background), "selected" (dark background / hover state)
MENU_IMAGES_PATHS = {
    "explore": {
        "default": "app/assets/images/home/menu/ExploreDefault.png",
        "selected": "app/assets/images/home/menu/exploreSelect.png",
    },
    "profile": {
        "default": "app/assets/images/home/menu/ProfileDefault.png",
        "selected": "app/assets/images/home/menu/profileSelect.png",
    },
    "notifications": {
        "default": "app/assets/images/home/menu/NotificationsDefault.png",
        "selected": "app/assets/images/home/menu/notificationsSelect.png",
    },
    "manage": {
        "default": "app/assets/images/home/menu/ManageDefault.png",
        "selected": "app/assets/images/home/menu/manageSelect.png",
    },
    "signOut": {
        "default": "app/assets/images/home/menu/signOutDefault.png",
        "selected": "app/assets/images/home/menu/signOutSelect.png",
    },
}

# Menu layout positioning
MENU_LAYOUT = {
    "gap": 50,
    "admin_start_x": 293,  # Centered for admin (5 items): (1350 - (5*113 + 4*50)) / 2 ≈ 292.5
    "regular_start_x": 374,  # Centered for regular (4 items): (1350 - (4*113 + 3*50)) / 2 = 374
    "menu_y": 310,
}
