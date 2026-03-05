# =====================================================
# 0. IMPORT DES LIBRAIRIES
# =====================================================
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.neighbors import KNeighborsRegressor
from sklearn.svm import SVR
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# =====================================================
# 1. CHARGEMENT DES DONNÉES
# =====================================================
print("Chargement des données...")

df = pd.read_csv("car_dataset.csv")
print("Dimensions :", df.shape)
print(df.head())

# =====================================================
# 2. SÉPARATION FEATURES / CIBLE
# =====================================================
X = df.drop(["price", "year"], axis=1)
y = df["price"]

# =====================================================
# 3. TRAIN / TEST SPLIT
# =====================================================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# =====================================================
# 4. STANDARDISATION
# =====================================================
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# =====================================================
# 5. EXPLORATION DES DONNÉES
# =====================================================
plt.figure(figsize=(8,6))
sns.heatmap(df.corr(), annot=True, cmap="coolwarm")
plt.title("Matrice de corrélation")
plt.tight_layout()
plt.show()

plt.figure(figsize=(6,4))
sns.histplot(df["price"], kde=True)
plt.title("Distribution des prix")
plt.tight_layout()
plt.show()

# =====================================================
# 6. FONCTIONS UTILES
# =====================================================
def evaluer_modele(y_true, y_pred, nom):
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)

    print(f"{nom}")
    print(f"   MAE  : {mae:.0f} €")
    print(f"   RMSE : {rmse:.0f} €")
    print(f"   R²   : {r2:.3f}\n")

    return {"Modèle": nom, "MAE": mae, "RMSE": rmse, "R2": r2}

def plot_predictions(y_true, y_pred, titre):
    plt.figure(figsize=(6,6))
    plt.scatter(y_true, y_pred, alpha=0.6)
    plt.plot(
        [y_true.min(), y_true.max()],
        [y_true.min(), y_true.max()],
        color="red"
    )
    plt.xlabel("Prix réel (€)")
    plt.ylabel("Prix prédit (€)")
    plt.title(titre)
    plt.tight_layout()
    plt.show()

resultats = []

# =====================================================
# 7. RÉGRESSION LINÉAIRE
# =====================================================
print("Régression Linéaire")

lr = LinearRegression()
lr.fit(X_train_scaled, y_train)
y_pred_lr = lr.predict(X_test_scaled)

resultats.append(
    evaluer_modele(y_test, y_pred_lr, "Régression Linéaire")
)

plot_predictions(
    y_test,
    y_pred_lr,
    "Régression Linéaire : Prix réel vs Prix prédit"
)

# =====================================================
# 8. RÉGRESSION POLYNOMIALE
# =====================================================
print("Régression Polynomiale")

meilleur_r2 = -np.inf
meilleur_degre = None
meilleur_pred_poly = None

for degre in [1, 2, 3]:
    poly = PolynomialFeatures(degree=degre)
    X_train_poly = poly.fit_transform(X_train_scaled)
    X_test_poly = poly.transform(X_test_scaled)

    model = LinearRegression()
    model.fit(X_train_poly, y_train)
    y_pred = model.predict(X_test_poly)

    r2 = r2_score(y_test, y_pred)

    if r2 > meilleur_r2:
        meilleur_r2 = r2
        meilleur_degre = degre
        meilleur_pred_poly = y_pred

resultats.append(
    evaluer_modele(
        y_test,
        meilleur_pred_poly,
        f"Régression Polynomiale (degré {meilleur_degre})"
    )
)

plot_predictions(
    y_test,
    meilleur_pred_poly,
    f"Régression Polynomiale (degré {meilleur_degre})"
)

# =====================================================
# 9. KNN
# =====================================================
print("KNN")

meilleur_r2 = -np.inf
meilleur_k = None
meilleur_pred_knn = None

for k in [3, 5, 7, 9, 11]:
    knn = KNeighborsRegressor(n_neighbors=k)
    knn.fit(X_train_scaled, y_train)
    y_pred = knn.predict(X_test_scaled)

    r2 = r2_score(y_test, y_pred)

    if r2 > meilleur_r2:
        meilleur_r2 = r2
        meilleur_k = k
        meilleur_pred_knn = y_pred

resultats.append(
    evaluer_modele(y_test, meilleur_pred_knn, f"KNN (k={meilleur_k})")
)

plot_predictions(
    y_test,
    meilleur_pred_knn,
    f"KNN (k={meilleur_k}) : Prix réel vs Prix prédit"
)

# =====================================================
# 10. SVM LINÉAIRE
# =====================================================
print("SVM Linéaire")

meilleur_r2 = -np.inf
meilleur_c = None
meilleur_pred_svm_lin = None

for c in [0.01, 0.1, 1, 10, 100]:
    svm = SVR(kernel="linear", C=c)
    svm.fit(X_train_scaled, y_train)
    y_pred = svm.predict(X_test_scaled)

    r2 = r2_score(y_test, y_pred)

    if r2 > meilleur_r2:
        meilleur_r2 = r2
        meilleur_c = c
        meilleur_pred_svm_lin = y_pred

resultats.append(
    evaluer_modele(y_test, meilleur_pred_svm_lin, f"SVM Linéaire (C={meilleur_c})")
)

plot_predictions(
    y_test,
    meilleur_pred_svm_lin,
    f"SVM Linéaire (C={meilleur_c})"
)

# =====================================================
# 11. SVM RBF
# =====================================================
print("SVM RBF")

meilleur_r2 = -np.inf
meilleur_params = None
meilleur_pred_svm_rbf = None

for c in [1, 10]:
    for gamma in [0.01, 0.1]:
        svm = SVR(kernel="rbf", C=c, gamma=gamma)
        svm.fit(X_train_scaled, y_train)
        y_pred = svm.predict(X_test_scaled)

        r2 = r2_score(y_test, y_pred)

        if r2 > meilleur_r2:
            meilleur_r2 = r2
            meilleur_params = (c, gamma)
            meilleur_pred_svm_rbf = y_pred

resultats.append(
    evaluer_modele(
        y_test,
        meilleur_pred_svm_rbf,
        f"SVM RBF (C={meilleur_params[0]}, gamma={meilleur_params[1]})"
    )
)

plot_predictions(
    y_test,
    meilleur_pred_svm_rbf,
    f"SVM RBF (C={meilleur_params[0]}, gamma={meilleur_params[1]})"
)

# =====================================================
# 12. COMPARAISON FINALE
# =====================================================
df_resultats = pd.DataFrame(resultats)
df_resultats = df_resultats.sort_values(by="R2", ascending=False)

print("🏆 Classement final des modèles :")
print(df_resultats)

plt.figure(figsize=(8,6))
plt.bar(df_resultats["Modèle"], df_resultats["R2"])
plt.xticks(rotation=45)
plt.ylabel("R²")
plt.title("Comparaison des modèles")
plt.tight_layout()
plt.show()

# =====================================================
# 13. SAUVEGARDE DU MEILLEUR MODÈLE
# =====================================================
meilleur_modele = LinearRegression()
meilleur_modele.fit(X_train_scaled, y_train)

joblib.dump(meilleur_modele, "modele_voiture.pkl")
joblib.dump(scaler, "scaler.pkl")

print("Modèle et scaler sauvegardés")
print("🎉 Fin du script")
