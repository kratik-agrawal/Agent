from flask import Flask, request, redirect, jsonify
from flask_cors import CORS

import time
import random
import secrets
import string

app = Flask(__name__)
CORS(app)

url_map = {}


def generate_random_alphanumeric(length):
    """
    Generates a random alphanumeric string of a specified length.

    Args:
        length (int): The desired length of the alphanumeric string.

    Returns:
        str: A randomly generated alphanumeric string.
    """
    characters = string.ascii_letters + string.digits
    random_string = ''.join(secrets.choice(characters) for i in range(length))
    return random_string

@app.route('/time')
def get_current_time():
    print("get_current_time")
    return jsonify({'time': time.time()})

@app.route('/shorten' , methods=['POST'])
def shorten_url():
    data = request.get_json()
    print(data)
    if data:
        url = data.get('url')
    print(url)

    # alpha numberic sequence
    while True:
        short_id = generate_random_alphanumeric(7)
        if short_id not in url_map:
            break
    
    url_map[short_id] = url

    #return localhost:8082/short_id
    shortened_url = "http://127.0.0.1:5000/" + str(short_id)

    return jsonify(shortened_url=shortened_url)
    
@app.route('/<short_id>' , methods=['GET'])
def return_long_url(short_id):
    if short_id in url_map: 
        return redirect(url_map[short_id])
    
    return redirect("google.com", code=404)


if __name__ == '__main__':
    app.run()

