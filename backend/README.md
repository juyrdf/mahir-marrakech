# Mahir Marrakech Backend

## 🚀 Deployment (Render)

1.  **Push to GitHub**:
    ```bash
    git add .
    git commit -m "Update"
    git push origin main
    ```
2.  **Create Service on Render**:
    - Go to [dashboard.render.com](https://dashboard.render.com)
    - Select **New +** -> **Web Service**
    - Connect your GitHub repo (`mahir-backend`)
    - **Runtime**: Docker
    - **Environment Variables**:
        - `PROJECT_NAME`: Mahir Marrakech
        - `GOOGLE_API_KEY`: [Your Key]
        - `PINECONE_API_KEY`: [Your Key]
3.  **Deploy**: Click "Create Web Service".

## Setup
1. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run Local Server:
   ```bash
   uvicorn app.main:app --reload
   ```

## Structure
- `/app`: Main application logic
- `/app/routers`: API endpoints
- `/app/core`: Configuration & Security
