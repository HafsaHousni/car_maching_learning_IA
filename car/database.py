import pymongo
import hashlib
from datetime import datetime

# =========================================================
# 1. CONNEXION AU SERVEUR
# =========================================================
# Si vous utilisez MongoDB Atlas (Cloud), remplacez l'adresse ci-dessous.
# Pour une installation locale, gardez "localhost".
MONGO_URI = "mongodb://localhost:27017/"

def get_db_connection():
    try:
        client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
        client.server_info() # Déclenche une exception si pas de connexion
        return client["garage_db"] # Nom de la base de données
    except Exception as e:
        print(f"Erreur de connexion MongoDB : {e}")
        return None

db = get_db_connection()

# =========================================================
# 2. INITIALISATION DES DONNÉES (SEEDING)
# =========================================================
def init_database():
    if db is None:
        return
    
    # --- A. Création de l'Admin (Sécurité) ---
    # On vérifie si la collection 'users' est vide ou si l'admin existe déjà
    if db.users.count_documents({"username": "admin"}) == 0:
        print("Création de l'utilisateur Admin...")
        # Hashage du mot de passe en SHA256 (ne jamais stocker en clair !)
        password_hache = hashlib.sha256("admin123".encode()).hexdigest()
        
        db.users.insert_one({
            "username": "admin",
            "password": password_hache,
            "role": "Directeur",
            "created_at": datetime.now()
        })

    # --- B. Remplissage du Showroom (Catalogue) ---
    # On vérifie si la collection 'showroom' est vide
    if db.showroom.count_documents({}) == 0:
        print("Remplissage du Showroom...")
        voitures_demo = [
            {
                "brand": "Audi", 
                "model": "RS3 Sportback", 
                "price": 45000, 
                "image_url": "https://images.unsplash.com/photo-1603584173870-7f23fdae1b7a?auto=format&fit=crop&w=500&q=60", 
                "specs": "2.5 TFSI 400ch",
                "status": "En vente"
            },
            {
                "brand": "BMW", 
                "model": "M4 Competition", 
                "price": 82000, 
                "image_url": "https://images.unsplash.com/photo-1617788138017-80ad40651399?auto=format&fit=crop&w=500&q=60", 
                "specs": "3.0 Biturbo 510ch",
                "status": "En vente"
            },
            {
                "brand": "Mercedes", 
                "model": "AMG GT", 
                "price": 115000, 
                "image_url": "https://images.unsplash.com/photo-1618843479313-40f8afb4b4d8?auto=format&fit=crop&w=500&q=60", 
                "specs": "V8 Biturbo",
                "status": "Réservé"
            },
            {
                "brand": "Porsche", 
                "model": "911 Carrera", 
                "price": 130000, 
                "image_url": "https://images.unsplash.com/photo-1503376763036-066120622c74?auto=format&fit=crop&w=500&q=60", 
                "specs": "Flat-6 385ch",
                "status": "En vente"
            }
        ]
        db.showroom.insert_many(voitures_demo)

# On lance l'initialisation au démarrage
init_database()

# =========================================================
# 3. FONCTIONS UTILISATEUR (CRUD)
# =========================================================

def verifier_login(username, password_brut):
    """Vérifie si le login/mdp correspond à un utilisateur en base"""
    if db is None: return None
    
    # On hache le mot de passe entré pour le comparer à celui en base
    pwd_hash = hashlib.sha256(password_brut.encode()).hexdigest()
    
    # Requête MongoDB : find_one
    user = db.users.find_one({
        "username": username, 
        "password": pwd_hash
    })
    return user # Retourne le dictionnaire user ou None

def ajouter_historique(username, voiture_desc, prix_estime):
    """Ajoute une ligne dans l'historique de recherche"""
    if db is None: return
    
    log = {
        "username": username,
        "car_model": voiture_desc,
        "price_estimated": float(prix_estime),
        "date_search": datetime.now()
    }
    # Requête MongoDB : insert_one
    db.history.insert_one(log)

def lire_historique(username):
    """Récupère les 10 dernières recherches de l'utilisateur"""
    if db is None: return []
    
    # Requête MongoDB : find + sort + limit
    cursor = db.history.find({"username": username})\
                       .sort("date_search", -1)\
                       .limit(10)
    return list(cursor)

def lire_showroom():
    """Récupère toutes les voitures du showroom"""
    if db is None: return []
    
    return list(db.showroom.find())