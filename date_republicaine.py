"""Calcul de la date du calendrier républicain et publication sur X."""
import os
import sys
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

# Jour 1 vendémiaire an I = 22 septembre 1792
EPOQUE = date(1792, 9, 22)

MOIS = ["vendémiaire", "brumaire", "frimaire", "nivôse", "pluviôse", "ventôse",
        "germinal", "floréal", "prairial", "messidor", "thermidor", "fructidor"]

JOURS_DECADE = ["Primidi", "Duodi", "Tridi", "Quartidi", "Quintidi",
                "Sextidi", "Septidi", "Octidi", "Nonidi", "Décadi"]

# Noms des jours, avec leur article (pour former « du », « de la », « de l' »)
_NOMS_BRUTS = """
le Raisin|le Safran|la Châtaigne|la Colchique|le Cheval|la Balsamine|la Carotte|l'Amaranthe|le Panais|la Cuve|la Pomme de terre|l'Immortelle|le Potiron|le Réséda|l'Âne|la Belle de nuit|la Citrouille|le Sarrasin|le Tournesol|le Pressoir|le Chanvre|la Pêche|le Navet|l'Amaryllis|le Bœuf|l'Aubergine|le Piment|la Tomate|l'Orge|le Tonneau
la Pomme|le Céleri|la Poire|la Betterave|l'Oie|l'Héliotrope|la Figue|la Scorsonère|l'Alisier|la Charrue|le Salsifis|la Macre|le Topinambour|l'Endive|le Dindon|le Chervis|le Cresson|la Dentelaire|la Grenade|la Herse|la Bacchante|l'Azerole|la Garance|l'Orange|le Faisan|la Pistache|le Macjonc|le Coing|le Cormier|le Rouleau
la Raiponce|le Turneps|la Chicorée|la Nèfle|le Cochon|la Mâche|le Chou-fleur|le Miel|le Genièvre|la Pioche|la Cire|le Raifort|le Cèdre|le Sapin|le Chevreuil|l'Ajonc|le Cyprès|le Lierre|la Sabine|le Hoyau|l'Érable à sucre|la Bruyère|le Roseau|l'Oseille|le Grillon|le Pignon|le Liège|la Truffe|l'Olive|la Pelle
la Tourbe|la Houille|le Bitume|le Soufre|le Chien|la Lave|la Terre végétale|le Fumier|le Salpêtre|le Fléau|le Granit|l'Argile|l'Ardoise|le Grès|le Lapin|le Silex|la Marne|la Pierre à chaux|le Marbre|le Van|la Pierre à plâtre|le Sel|le Fer|le Cuivre|le Chat|l'Étain|le Plomb|le Zinc|le Mercure|le Crible
la Lauréole|la Mousse|le Fragon|le Perce-neige|le Taureau|le Laurier-thym|l'Amadouvier|le Mézéréon|le Peuplier|la Cognée|l'Ellébore|le Brocoli|le Laurier|l'Avelinier|la Vache|le Buis|le Lichen|l'If|la Pulmonaire|la Serpette|le Thlaspi|le Thymelé|le Chiendent|la Traînasse|le Lièvre|la Guède|le Noisetier|le Cyclamen|la Chélidoine|le Traîneau
le Tussilage|le Cornouiller|le Violier|le Troène|le Bouc|l'Asaret|l'Alaterne|la Violette|le Marceau|la Bêche|le Narcisse|l'Orme|la Fumeterre|le Vélar|la Chèvre|l'Épinard|le Doronic|le Mouron|le Cerfeuil|le Cordeau|la Mandragore|le Persil|le Cochléaria|la Pâquerette|le Thon|le Pissenlit|la Sylvie|le Capillaire|le Frêne|le Plantoir
la Primevère|le Platane|l'Asperge|la Tulipe|la Poule|la Bette|le Bouleau|la Jonquille|l'Aulne|le Couvoir|la Pervenche|le Charme|la Morille|le Hêtre|l'Abeille|la Laitue|le Mélèze|la Ciguë|le Radis|la Ruche|le Gainier|la Romaine|le Marronnier|la Roquette|le Pigeon|le Lilas|l'Anémone|la Pensée|la Myrtille|le Greffoir
la Rose|le Chêne|la Fougère|l'Aubépine|le Rossignol|l'Ancolie|le Muguet|le Champignon|l'Hyacinthe|le Râteau|la Rhubarbe|le Sainfoin|le Bâton-d'or|le Chamérops|le Ver à soie|la Consoude|la Pimprenelle|la Corbeille d'or|l'Arroche|le Sarcloir|le Statice|la Fritillaire|la Bourrache|la Valériane|la Carpe|le Fusain|la Civette|la Buglosse|le Sénevé|la Houlette
la Luzerne|l'Hémérocalle|le Trèfle|l'Angélique|le Canard|la Mélisse|le Fromental|le Martagon|le Serpolet|la Faux|la Fraise|la Bétoine|le Pois|l'Acacia|la Caille|l'Œillet|le Sureau|le Pavot|le Tilleul|la Fourche|le Barbeau|la Camomille|le Chèvrefeuille|le Caille-lait|la Tanche|le Jasmin|la Verveine|le Thym|la Pivoine|le Chariot
le Seigle|l'Avoine|l'Oignon|la Véronique|le Mulet|le Romarin|le Concombre|l'Échalote|l'Absinthe|la Faucille|la Coriandre|l'Artichaut|la Girofle|la Lavande|le Chamois|le Tabac|la Groseille|la Gesse|la Cerise|le Parc|la Menthe|le Cumin|le Haricot|l'Orcanète|la Pintade|la Sauge|l'Ail|la Vesce|le Blé|la Chalémie
l'Épeautre|le Bouillon blanc|le Melon|l'Ivraie|le Bélier|la Prêle|l'Armoise|le Carthame|la Mûre|l'Arrosoir|le Panic|la Salicorne|l'Abricot|le Basilic|la Brebis|la Guimauve|le Lin|l'Amande|la Gentiane|l'Écluse|la Carline|le Câprier|la Lentille|l'Aunée|la Loutre|le Myrte|le Colza|le Lupin|le Coton|le Moulin
la Prune|le Millet|le Lycoperdon|l'Escourgeon|le Saumon|la Tubéreuse|le Sucrion|l'Apocyn|la Réglisse|l'Échelle|la Pastèque|le Fenouil|l'Épine vinette|la Noix|la Truite|le Citron|la Cardère|le Nerprun|la Tagette|la Hotte|l'Églantier|la Noisette|le Houblon|le Sorgho|l'Écrevisse|la Bigarade|la Verge d'or|le Maïs|le Marron|le Panier
"""
NOMS = [ligne.split("|") for ligne in _NOMS_BRUTS.strip().splitlines()]
assert len(NOMS) == 12 and all(len(m) == 30 for m in NOMS)

COMPLEMENTAIRES = ["de la Vertu", "du Génie", "du Travail", "de l'Opinion",
                   "des Récompenses", "de la Révolution"]

# Années sextiles historiques (règle de l'équinoxe), puis règle de Romme dès l'an XX
SEXTILES_HISTORIQUES = {3, 7, 11, 15}


def est_sextile(an):
    if an < 20:
        return an in SEXTILES_HISTORIQUES
    return an % 4 == 0 and (an % 100 != 0 or an % 400 == 0)


# Périodes où la France était en république (dates de début et de fin incluses).
# Premier Empire, Restauration, monarchie de Juillet et Second Empire en sont
# exclus. Vichy n'interrompt pas la République : selon l'ordonnance du
# 9 août 1944, la République n'a jamais cessé d'exister (France libre).
REPUBLIQUES = [
    (date(1792, 9, 22), date(1804, 5, 17)),   # Ire République
    (date(1848, 2, 24), date(1852, 12, 1)),   # IIe République
    (date(1870, 9, 4), date(9999, 12, 31)),   # IIIe République et suivantes
]


def debut_annee(an):
    """Date grégorienne du 1er vendémiaire de l'an donné."""
    d = EPOQUE
    for a in range(1, an):
        d += timedelta(days=366 if est_sextile(a) else 365)
    return d


def an_republicain(an):
    """Rang de l'année en ne comptant que les années ayant connu la République.

    Une année est comptée si au moins un de ses jours tombe sous un régime
    républicain ; les années entièrement passées sous un empire, une monarchie
    ou le régime de Vichy sont ignorées.
    """
    rang = 0
    for a in range(1, an + 1):
        debut = debut_annee(a)
        fin = debut_annee(a + 1) - timedelta(days=1)
        if any(debut <= f and d <= fin for d, f in REPUBLIQUES):
            rang += 1
    return rang


def romain(n):
    valeurs = [(1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"),
               (90, "XC"), (50, "L"), (40, "XL"), (10, "X"), (9, "IX"),
               (5, "V"), (4, "IV"), (1, "I")]
    s = ""
    for v, r in valeurs:
        while n >= v:
            s += r
            n -= v
    return s


def avec_de(nom):
    """« le Raisin » -> « du Raisin », « la Pêche » -> « de la Pêche »…"""
    if nom.startswith("le "):
        return "du " + nom[3:]
    if nom.startswith("la "):
        return "de la " + nom[3:]
    if nom.startswith("l'"):
        return "de " + nom
    return "de " + nom


def date_republicaine(d):
    jours = (d - EPOQUE).days
    an = 1
    while True:
        duree = 366 if est_sextile(an) else 365
        if jours < duree:
            break
        jours -= duree
        an += 1
    return an, jours  # jours = rang dans l'année, à partir de 0


def ordinal(n):
    return "1er" if n == 1 else f"{n}e"


def message(d):
    an, j = date_republicaine(d)
    rang = an_republicain(an)
    annee = f"an {romain(rang)} ({rang})"
    if j < 360:
        mois, jour = divmod(j, 30)
        nom = avec_de(NOMS[mois][jour])
        nom_jour = JOURS_DECADE[jour % 10]
        article = "l'" if nom_jour == "Octidi" else "le "
        numero = "1er" if jour == 0 else str(jour + 1)
        return (f"Aujourd'hui, nous sommes {article}{nom_jour} "
                f"{numero} {MOIS[mois]} de l'{annee}, jour {nom}.")
    k = j - 360
    return (f"Aujourd'hui, nous sommes le {ordinal(k + 1)} jour complémentaire "
            f"de l'{annee}, jour {COMPLEMENTAIRES[k]}.")


def publier(texte):
    import tweepy
    client = tweepy.Client(
        consumer_key=os.environ["X_API_KEY"],
        consumer_secret=os.environ["X_API_SECRET"],
        access_token=os.environ["X_ACCESS_TOKEN"],
        access_token_secret=os.environ["X_ACCESS_TOKEN_SECRET"],
    )
    client.create_tweet(text=texte)


if __name__ == "__main__":
    aujourdhui = datetime.now(ZoneInfo("Europe/Paris")).date()
    texte = message(aujourdhui)
    print(texte)
    if "--publier" in sys.argv:
        publier(texte)
