Estrutura do projeto:

VODplayer/
├── data/
│   ├── cache/
│       ├── m3u8_files/
│           └── index.m3u8
│       └── sample_streamer_page.html
│   ├── favorites.json
│   └── history.json
├── logs/
│   ├── app.log
│   ├── main_app.log
│   └── __init__.py
├── resources/
│   ├── icons/
│   └── styles/
├── ui/
│   ├── __pycache__/
│   ├── main_window.py
│   ├── video_player_widget.py
│   ├── vod_list_widget.py
│   └── __init__.py
├── utils/
    ├── __pycache__/
    ├── downloader.py
    ├── logger.py
    ├── scraper.py
    └── __init__.py
├── .gitignore
├── main.py
└── __init__.py