import unittest
import MySQLdb
import redis
import requests
import json


class TestBugspad(unittest.TestCase):

    """
    This class contain the test cases for bugspad.
    """

    def test_insert_bug(self):

        # Run insert bug API
        url = "http://127.0.0.1:9998/bug/"
        summary = "This is a test bug"
        text = "Please don't expect from this bug"
        component_id = "3431"
        d = {'user': 'kumarpraveen.nitdgp@gmail.com',
             "password": 'asdf',
             "summary": summary,
             "description": text,
             "component_id": component_id
             }

        response = requests.post(url, data=json.dumps(d))
        if response.text:
            bug_id = str(response.text).strip()
        else:
            print "Looks like bugspad server is down."

        # Get the redis connection,make sure redis serice is running
        bug_data = redis.StrictRedis()

        # Get the json value of stored  key
        redis_bug_detail = bug_data.hgetall('bugs')[bug_id]


        """
        Connect to Database and get the information about inserted data.
        Connect to redis and get the information about data

        """
        db = MySQLdb.connect(host = "localhost",
                            user = "root",
                            passwd = "",
                            db = "bugzilla")

        # Create the cursor object.
        cur = db.cursor()

        # Use SQL queries to execute with cursor
        cur.execute("Select * From bugs where id=%s" % bug_id)

        # Print all the bug ID
        ((bug_id,status,version,
        severity,hardware,priority,
        reporter,qa,docs,whiteboard,
        summary,description,reported,
        fixedinver,component_id),) = cur.fetchall()

        # Compare radis data with mysql database
        database_bug_detail = dict (zip(("id","status","summary"),
                                       (bug_id, status, summary)))
        shared_items = set(database_bug_detail.items()) ^ \
                            set(json.loads(redis_bug_detail).items())

        self.assertEqual(len(shared_items), 0)




if __name__ == '__main__':
    unittest.main()
