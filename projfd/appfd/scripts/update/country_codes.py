from datetime import datetime
from django.db import connection

def run(debug=False):

    try:

        if debug:
            print("starting update.country_codes")
            start = datetime.now()

        connection.cursor().execute("SELECT update_country_codes();")

        if debug:
            duration_in_seconds = (datetime.now() - start).total_seconds()
            if duration_in_seconds < 60:
                if debug: print("updating country_codes took", duration_in_seconds, "seconds")
            else:
                if debug: print("updating country_codes took", duration_in_seconds / 60, "minutes")

    except Exception as e:

        print(e)
