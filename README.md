# MTA train delays/status web service

To run the app:
```
pip install -r requirements.txt
python app.py
```
While testing, if the MTA realtime feed is not updating (trains are running on time), please change the `_poll_api_data()` to `_poll_local_data()` within `main` and change the `data/status.txt` manually. You may need to save the text file for the changes to take effect.
