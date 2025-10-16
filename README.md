<<<<<<< HEAD
Movie Ticket Final - Flask + React + Stripe + OpenAI Chat

Run Backend:
1. cd backend
2. python -m venv venv
3. venv\Scripts\activate   (Windows)
4. pip install -r requirements.txt
5. set STRIPE_SECRET_KEY=sk_test_yourkey
   set OPENAI_API_KEY=sk-...   (optional)
6. python app.py

Run Frontend:
1. cd frontend
2. npm install
3. In frontend/src/config.js replace STRIPE_PUBLISHABLE_KEY with your pk_test key
4. npm start

Notes:
- Posters are stored in backend/posters as SVG placeholders.
- This demo uses in-memory bookings; restart loses data.
- For production use persistent DB and Stripe webhooks to verify payments securely.
=======
# movie-ticketbooking
>>>>>>> f4d0081038db13665ab8f5f0ebe712d9e6489364
