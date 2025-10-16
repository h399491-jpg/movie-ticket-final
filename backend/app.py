from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os, stripe, openai
from datetime import datetime

app = Flask(__name__, static_folder='../frontend/build', static_url_path='/')
CORS(app)

STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY','sk_test_PLACEHOLDER')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY','')

stripe.api_key = STRIPE_SECRET_KEY
openai.api_key = OPENAI_API_KEY

movies = [
    {"id":1,"title":"Leo","description":"A high-octane thriller.","poster":"/posters/leo.svg","price":250},
    {"id":2,"title":"Jailer","description":"A gripping drama.","poster":"/posters/jailer.svg","price":220},
    {"id":3,"title":"Kalki 2898 AD","description":"Sci-fi epic.","poster":"/posters/kalki.svg","price":300}
]
snacks = [{"id":1,"name":"Popcorn","price":120},{"id":2,"name":"Samosa","price":40},{"id":3,"name":"Fries","price":80},{"id":4,"name":"Cold Drink","price":70}]
BOOKINGS={}; NEXT_ID=1

@app.route('/api/movies')
def get_movies():
    return jsonify(movies)

@app.route('/api/snacks')
def get_snacks():
    return jsonify(snacks)

@app.route('/api/book', methods=['POST'])
def book():
    global NEXT_ID
    data = request.get_json() or {}
    movie_id = data.get('movie_id')
    seats = data.get('seats', [])
    snack_ids = data.get('snack_ids', [])
    user_name = data.get('user_name','Guest')
    movie = next((m for m in movies if m['id']==movie_id), None)
    if not movie:
        return jsonify({'error':'movie not found'}),400
    seats_price = movie.get('price',250) * max(1, len(seats))
    snacks_sel = [s for s in snacks if s['id'] in snack_ids]
    snacks_price = sum(s['price'] for s in snacks_sel)
    total = seats_price + snacks_price
    booking = {'id':NEXT_ID,'movie_id':movie_id,'seats':seats,'snacks':[s['name'] for s in snacks_sel],'amount':total,'user_name':user_name,'paid':False,'created_at':datetime.utcnow().isoformat()}
    BOOKINGS[NEXT_ID]=booking; NEXT_ID+=1
    return jsonify({'ok':True,'booking':booking})

@app.route('/api/create-payment-intent', methods=['POST'])
def create_payment_intent():
    data = request.get_json() or {}
    booking_id = data.get('booking_id')
    if not booking_id:
        return jsonify({'error':'booking_id required'}),400
    booking = BOOKINGS.get(int(booking_id))
    if not booking:
        return jsonify({'error':'booking not found'}),404
    try:
        intent = stripe.PaymentIntent.create(amount=int(booking['amount']*100),currency='inr',metadata={'booking_id':str(booking_id)})
        return jsonify({'clientSecret':intent.client_secret,'amount':booking['amount']})
    except Exception as e:
        return jsonify({'error':str(e)}),500

@app.route('/api/pay', methods=['POST'])
def mark_paid():
    data = request.get_json() or {}
    booking_id = data.get('booking_id')
    if not booking_id:
        return jsonify({'error':'booking_id required'}),400
    b = BOOKINGS.get(int(booking_id))
    if not b:
        return jsonify({'error':'booking not found'}),404
    b['paid']=True
    return jsonify({'ok':True,'booking':b})

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json() or {}
    msg = data.get('message','')
    if OPENAI_API_KEY:
        try:
            resp = openai.ChatCompletion.create(model='gpt-3.5-turbo',messages=[{'role':'system','content':'You are a helpful assistant.'},{'role':'user','content':msg}],max_tokens=400)
            reply = resp['choices'][0]['message']['content'].strip()
            return jsonify({'reply':reply})
        except Exception as e:
            return jsonify({'reply':'OpenAI error: '+str(e)}),500
    lc=msg.lower()
    if 'snack' in lc: return jsonify({'reply':'We have Popcorn, Samosa, Fries and Cold Drinks.'})
    if 'when' in lc: return jsonify({'reply':'Shows: 10:00,13:30,16:45,19:30'})
    return jsonify({'reply':'I can help with bookings and showtimes. Set OPENAI_API_KEY for full AI answers.'})

@app.route('/posters/<path:fname>')
def posters(fname):
    folder = os.path.join(os.path.dirname(__file__),'posters')
    return send_from_directory(folder, fname)

if __name__=='__main__':
    p=os.path.join(os.path.dirname(__file__),'posters'); os.makedirs(p,exist_ok=True)
    with open(os.path.join(p,'leo.svg'),'w') as f: f.write('<svg xmlns="http://www.w3.org/2000/svg" width="600" height="900"><rect width="100%" height="100%" fill="#1a1a2e"/><text x="50%" y="45%" fill="#fff" font-size="40" text-anchor="middle">LEO</text></svg>')
    with open(os.path.join(p,'jailer.svg'),'w') as f: f.write('<svg xmlns="http://www.w3.org/2000/svg" width="600" height="900"><rect width="100%" height="100%" fill="#2b2d42"/><text x="50%" y="45%" fill="#fff" font-size="36" text-anchor="middle">JAILER</text></svg>')
    with open(os.path.join(p,'kalki.svg'),'w') as f: f.write('<svg xmlns="http://www.w3.org/2000/svg" width="600" height="900"><rect width="100%" height="100%" fill="#0b3d91"/><text x="50%" y="45%" fill="#fff" font-size="30" text-anchor="middle">KALKI 2898 AD</text></svg>')
    print('Starting backend on http://127.0.0.1:5000')
    app.run(host='0.0.0.0', port=5000, debug=True)
