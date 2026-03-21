# Alimento

AI-powered nutrition platform with secure sign-in, meal intelligence, planning, and progress tracking.

Alimento helps people make better food decisions by turning meal data into practical guidance. Users can analyze meals, track nutrition trends, build plans, and receive personalized coaching in one web application.

![Alimento Interface](https://img.shields.io/badge/Status-Production%20Ready-brightgreen) ![Python](https://img.shields.io/badge/Python-3.12+-blue) ![Flask](https://img.shields.io/badge/Flask-2.3+-green) ![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-brightgreen)

## Product Overview

Alimento is a full-stack web application focused on day-to-day nutrition decision support.

- Analyze meals from image URL, text, barcode, or manual nutrition input.
- Convert meal logs into calorie and macro insights.
- Build weekly plans and reusable recipes.
- Track weight and consistency over time.
- Manage reminder settings and integration readiness from account settings.

## Core Capabilities

- **AI-Powered Analysis**: Instant nutrition breakdown (Calories, Macros, Micros) using Gemini 2.5 Flash Lite.
- **Global Dashboard**: Timezone-aware tracking for meals & hydration that works anywhere.
- **Personalized Goals**: Smart scoring & insights for Keto, Vegan, Paleo, and more.
- **Secure & Private**: Google OAuth, private history, and dedicated guest sessions.
- **Modern UX**: Responsive Glassmorphism design with Dark Mode support.

## Platform Features

- **Unified Meal Logging**: Image URL, text input, barcode, and manual macro logging.
- **Weekly Meal Planner**: Generate and edit weekly plans with auto grocery list generation.
- **Recipe Library**: Create, list, and manage private/public recipes with nutrition data.
- **Progress Tracking**: Daily trend summaries and body-weight logging endpoints.
- **Social Challenges**: Create/join challenges with leaderboard scoring.
- **Integrations + Reminders Settings**: Persisted user settings for reminders and integration status.
- **Migration Support**: Idempotent migration from legacy `analysis_history` to `meal_logs`.

## Quick Setup

### Prerequisites
- **Python 3.12+**
- **Google AI API key** (Gemini)
- **MongoDB Atlas** account
- **Google Cloud Console** project (for OAuth)

### Installation

1. **Clone & Environment Setup**
   ```bash
   git clone <repository-url>
   cd alimento
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Environment Configuration**
   Create `.env` file:
   ```env
   # AI Configuration
   GEMINI_API_KEY=your_google_ai_api_key
   
   # Database
   MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/alimento
   
   # Authentication
   GOOGLE_CLIENT_ID=your_google_oauth_client_id
   GOOGLE_CLIENT_SECRET=your_google_oauth_client_secret
   OAUTH_REDIRECT_URI=http://localhost:5001/auth/callback
   FLASK_SECRET_KEY=your_secure_secret_key
   
   # Optional
   ADMIN_EMAILS=admin@example.com,admin2@example.com
   ```

3. **Google Cloud Console Setup**
   - Create a new project or use existing
   - Enable Google OAuth and related identity APIs
   - Configure OAuth consent screen
   - Add authorized origins: `http://localhost:5001`
   - Add authorized redirect URIs: `http://localhost:5001/auth/callback`

4. **Database Setup**
   - Create MongoDB Atlas cluster
   - Whitelist your IP address
   - Get connection string and add to `.env`

5. **Run Application**
   ```bash
   source venv/bin/activate
   python app.py
   ```

6. **Access Application**
   ```
   http://localhost:5001
   ```

## Tech Stack

### Backend
- **Flask 2.3.2** - Web framework
- **Google Gemini 2.5 Flash Lite** - AI meal analysis and coaching
- **MongoDB Atlas + PyMongo 4.6** - Cloud database and driver
- **Flask-Login 0.6.3** - Session management
- **Authlib 1.2.0** - OAuth 2.0 implementation
- **Flask-WTF 1.1.1** - Form handling and CSRF protection
- **Flask-CORS 4.0** - Cross-origin resource sharing
- **Pillow 10.0** - Image processing

### Frontend
- **Tailwind CSS v3.4** - Utility-first styling (CDN)
- **Phosphor Icons** - Modern icon set
- **Geist + Playfair Display** - Typography (Google Fonts)
- **Vanilla JavaScript** - Interactive functionality
- **Responsive Design** - Mobile-first approach

### Security & Auth
- **Google OAuth 2.0** - Secure authentication
- **Session cookies** - Secure user sessions
- **CSRF protection** - Form security via Flask-WTF
- **Usage rate limiting** - Prevent abuse

### Deployment
- **Vercel-ready** configuration
- **Environment variable** support
- **Static file** optimization
- **Production** security settings



## Security Features

### Authentication
- **Google OAuth 2.0** - Industry standard security
- **Secure session** management
- **HTTPS-ready** for production
- **CSRF protection** on forms

### Privacy
- **User data isolation** - strict ownership rules
- **Guest session** isolation with signed cookies
- **IP and browser** tracking for security
- **No cross-user** data leakage

### Rate Limiting
- **Daily usage limits** to prevent abuse
- **Per-user tracking** with MongoDB
- **Graceful limit** notifications

## Deployment

### Vercel (Recommended)
1. **Connect repository** to Vercel
2. **Add environment variables** in dashboard
3. **Deploy automatically** on push

### Manual Deployment
1. **Set PRODUCTION=true** in environment
2. **Configure HTTPS** and secure cookies
3. **Update OAuth redirects** for production domain
4. **Monitor usage** and performance

## Contributing

1. **Fork the repository**
2. **Create feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit changes** (`git commit -m 'Add amazing feature'`)
4. **Push to branch** (`git push origin feature/amazing-feature`)
5. **Open Pull Request**