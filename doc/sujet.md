# Sujet de projet

## Projet VeloScope

Tuteur : André Rivière

### Présentation

Les vélos en libre-service sont disponibles en temps réel dans de nombreuses villes. Pourtant, une simple carte des stations ne permet pas vraiment de répondre à des questions utiles :
À quelle heure vais-je réellement trouver un vélo ?
Quelles stations sont souvent pleines ?
Quels trajets sont les plus fiables ?
Est-ce qu'une station est régulièrement vide le matin mais pleine le soir ?
Le projet VeloScope consiste à développer une API permettant de collecter, historiser et analyser les données de vélos en libre-service d'une ville.
L'application récupère périodiquement les informations d'une API de vélos en libre-service compatible avec le standard GBFS : stations, nombre de vélos disponibles, nombre de places libres, vélos électriques, etc.
Contrairement à une simple application de consultation, VeloScope doit construire son propre historique afin de permettre des analyses temporelles et de produire des indicateurs de fiabilité des stations.

### Fonctionnalités

- F1 : Gestion des utilisateurs
 Un utilisateur peut :
  - créer un compte ;
  - se connecter ;
  - consulter les données et statistiques ;
  - gérer ses stations favorites.
 Un compte ADMIN peut gérer les utilisateurs.
- F2 : Collecte des données
 L'application doit interroger régulièrement l'API GBFS choisie et récupérer les informations des stations.
 Pour chaque relevé, on stockera notamment :
  - station ;
  - date et heure ;
  - nombre de vélos disponibles ;
  - nombre de places disponibles ;
  - nombre de vélos électriques ;
  - état de la station.
 Les données récupérées doivent être historisées en base PostgreSQL.
 L'application ne doit pas simplement remplacer les valeurs précédentes : elle doit permettre de reconstruire l'état du réseau à différents instants.
- F3 : Consultation d'une station
 L'utilisateur peut rechercher une station et consulter :
  - son état actuel ;
  - son nombre de vélos disponibles ;
  - sa capacité ;
  - son taux de remplissage ;
  - l'évolution de sa disponibilité sur une période donnée.
 L'utilisateur doit notamment pouvoir choisir une période :
  - dernières 24 heures ;
  - 7 derniers jours ;
  - 30 derniers jours.
- F4 : Score de fiabilité des stations
 C'est la fonctionnalité métier principale.
 Pour chaque station, l'application calcule un score de fiabilité.
 Par exemple, une station est considérée comme :
  - vide lorsqu'il n'y a plus de vélo disponible ;
  - saturée lorsqu'il ne reste plus de place ;
  - fonctionnelle dans les autres cas.
 À partir de l'historique, l'application calcule notamment :
  - pourcentage du temps passé vide ;
  - pourcentage du temps passé saturé ;
  - durée moyenne des épisodes de saturation ;
  - durée moyenne des épisodes de pénurie ;
  - évolution du score au cours du temps.
 Le score global est défini par les étudiants à partir d'une formule documentée.
- F5 : Recommandation de station
 Lorsqu'un utilisateur demande :
 « Je veux prendre un vélo à proximité »
 l'API doit être capable de lui proposer plusieurs stations pertinentes.
 La recommandation doit prendre en compte plusieurs critères, par exemple :
  - distance ;
  - nombre de vélos actuellement disponibles ;
  - fiabilité historique de la station ;
  - disponibilité de vélos électriques ;
  - tendance récente de la station.
 Deux stations à distance équivalente ne doivent donc pas nécessairement être classées de la même manière.
 La formule de classement devra être justifiée et testée.

### Fonctionnalités optionnelles

- FO1 : Prévision de disponibilité
    À partir de l'historique, tenter d'estimer la probabilité qu'une station     soit vide ou saturée dans les prochaines heures.
    Il est possible de commencer avec un modèle statistique très simple avant d'utiliser une approche plus avancée.
- FO2 : Heatmap du réseau
 Proposer une visualisation géographique permettant d'identifier :
  - les zones où les stations sont souvent saturées ;
  - les zones où les stations sont souvent vides ;
  - les stations les plus fiables.
 Une carte interactive peut être proposée.
- FO3 : Détection d'anomalies
 Détecter automatiquement les comportements inhabituels :
  - station qui ne transmet plus de données ;
  - variation impossible du nombre de vélos ;
  - station bloquée dans le même état pendant une longue période ;
  - apparition/disparition inhabituelle de vélos.
    L'API doit pouvoir signaler ces anomalies.
- FO4 : Assistant de trajet
 L'utilisateur renseigne :
 station de départ + station d'arrivée
 et l'application propose plusieurs stratégies :
 rapide, fiable, vélo électrique, ou risque minimal.
 Chaque stratégie utilise une fonction de coût différente.
- FO5 : Défi entre utilisateurs
    Les utilisateurs peuvent comparer leurs habitudes :
  - nombre de trajets ;
  - distance parcourue ;
  - stations utilisées ;
  - nombre de trajets réalisés avec un vélo électrique ;
  - régularité d'utilisation.
 Des badges peuvent être attribués.

### API externe

L'API externe n'est pas imposée.
Les étudiants doivent identifier une ville proposant des données GBFS ouvertes, étudier sa documentation et intégrer son API.
L'intérêt pédagogique est justement de devoir :

1. comprendre une API inconnue ;
2. identifier les données pertinentes ;
3. gérer ses évolutions ou erreurs ;
4. construire une couche d'abstraction afin que l'application ne dépende pas directement d'une ville particulière.
