MATERIAL_ADMIN_SITE = {
    'HEADER':  'SINCEHENCE ADMIN',  # Admin site header
    'TITLE':  'SINCEHENCE LTD',  # Admin site title
    'FAVICON':  'favicon.ico',  # Admin site favicon (path to static should be specified)
    'MAIN_BG_COLOR':  '#511414',  # Admin site main color, css color should be specified
    'MAIN_HOVER_COLOR':  '#2f011d',  # Admin site main hover color, css color should be specified
    'PROFILE_PICTURE':  'icon.png',  # Admin site profile picture (path to static should be specified)
    'PROFILE_BG':  'pr_bg.png',  # Admin site profile background (path to static should be specified)
    'LOGIN_LOGO':  'icon.png',  # Admin site logo on login page (path to static should be specified)
    'LOGOUT_BG':  'pr_bg.png',  # Admin site background on login/logout pages (path to static should be specified)
    'SHOW_THEMES':  True,  #  Show default admin themes button
    'TRAY_REVERSE': True,  # Hide object-tools and additional-submit-line by default
    'NAVBAR_REVERSE': True,  # Hide side navbar by default
    'SHOW_COUNTS': True, # Show instances counts for each model
    'APP_ICONS': {  # Set icons for applications(lowercase), including 3rd party apps, {'application_name': 'material_icon_name', ...}
        'sites': 'send',
        'accounts' : 'account_circle',
        'core' : 'all_inclusive',
    },
    'MODEL_ICONS': {  # Set icons for models(lowercase), including 3rd party models, {'model_name': 'material_icon_name', ...}
        'site': 'contact_mail',
        'product' : 'inventory',
        'category' : 'category',
        'blog' : 'rss_feed',
        'contactmessage' : 'contacts',
        'currency' : 'attach_money',
        'attachment' : 'attach_file',
        'page' : 'description',
        'ourservice': 'compass_calibration'
    }
}