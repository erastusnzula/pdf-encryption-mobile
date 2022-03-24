import json

settings_json = json.dumps([
    {
        'type': 'title',
        'title': 'Settings'
    },

    {
        'type': 'numeric',
        'title': 'font size',
        'desc': 'Adjust font size',
        'section': 'Settings',
        'key': 'font_size',
    },
    {
        'type': 'options',
        'title': 'Fonts',
        'desc': 'Choose a font',
        'section': 'Settings',
        'key': 'font_name',
        'options': ['Eurostile.ttf', 'Sackers-Gothic-Std-Light.ttf', 'Lcd.ttf', 'Bullpen3D.ttf',
                    'Demo_ConeriaScript_Slanted.ttf',
                    'Montague.ttf', 'PlayfairDisplay-Black.ttf',
                    'PlayfairDisplay-Italic.ttf', 'PlayfairDisplay-Regular.ttf']
    },
])
