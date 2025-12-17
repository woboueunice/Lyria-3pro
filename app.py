from flask import Flask, jsonify
import google.generativeai as genai
import os
import requests

app = Flask(__name__)

# --- CONFIGURATION ---
api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

@app.route('/')
def home():
    return "🎵 Diagnostic Lyria (Musique) en ligne !"

@app.route('/check-music')
def check_music_model():
    if not api_key:
        return jsonify({"error": "Clé API manquante"}), 500

    results = {
        "status": "analyse_terminee",
        "has_lyria_access": False,
        "details": []
    }

    try:
        # 1. On cherche le modèle dans la liste officielle
        # Lyria est souvent caché ou en mode "preview"
        all_models = genai.list_models()
        found_in_list = False
        
        for m in all_models:
            if 'lyria' in m.name.lower() or 'music' in m.name.lower():
                found_in_list = True
                results['details'].append({
                    "name": m.name,
                    "methods": m.supported_generation_methods,
                    "description": m.description
                })

        # 2. Vérification Directe (Ping)
        # On essaie d'obtenir les infos du modèle précis même s'il est caché
        target_model = "models/lyria-realtime-exp"
        try:
            model_info = genai.get_model(target_model)
            results['has_lyria_access'] = True
            results['lyria_info'] = {
                "name": model_info.name,
                "description": model_info.description,
                "input_token_limit": model_info.input_token_limit
            }
        except Exception as e:
            results['details'].append(f"Impossible d'accéder directement à {target_model} : {str(e)}")

        # 3. Vérification via API REST (Méthode de secours)
        if not results['has_lyria_access']:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/lyria-realtime-exp?key={api_key}"
            response = requests.get(url)
            if response.status_code == 200:
                results['has_lyria_access'] = True
                results['details'].append("Accès confirmé via API REST (C'est bon signe !)")
            else:
                results['details'].append(f"Refus API REST: {response.status_code} - {response.text}")

        return jsonify(results)

    except Exception as e:
        return jsonify({"error": "Erreur critique", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
                
