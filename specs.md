<div align="center">
<img width=200 src="https://raw.githubusercontent.com/tienne-B/lavenue/master/logo.svg?sanitize=true">

# Lavenue
</div>

Pour la bonne gestion et sémantique d'assemblée déliberante, *Lavenue* est un logiciel proposé pour faciliter l'utilisation du *Code Lespérance* (CL) et d'automatiser l'application des décisions faites.

## Introduction
À la suite des instances de la FAÉCUM qui se déroulaient de manière virtuelle en hiver 2021, des failles importantes avec la capacité de pouvoir tenir ces rencontres sans outils à ces fins ont été soulèvés. Ces failles font que c'est plus dure aux participants de pouvoir facilement intéragir avec les procédures pour faire des propositions, ainsi que de connaitre l'ordre de parole qui est opaque.

### But
Ce logiciel va être basé sur l'internet avec deux grandes axes. La première est d'augmenter la transparence des assemblées en facilitant les interactions et demandes et de supporter la présidence et secrétariat avec leurs travaux. La deuxième est dans la géneration de documentation, pour automatiser les procès verbaux et des résolutions. Un effet tierce de cet éffort est la capacité d'analyser les assemblées en tant que données à des fins de recherche.

### Public cible et utilisation
*Lavenue* pourra être utilisé par les associations étudiantes qui utilisent le *Code Lespérance* ou des codes similaires. Ces associations l'utiliseront durant leurs assemblées par tout parti:
* les participants pour demander la parole et faire des propositions;
* la présidence pour accepter des tours de parole et prendre des actions;
* le secrétariat pour rédiger des sommaires des interventions.

Ce logiciel sera aussi utilisé au préalable par des officiers de l'association afin de mettre un horaire pour l'assemblée.

Entretemps, le public peut accèder aux ressources informationnelles comme les procès verbaux qui ont été rédigés sur la plateforme.

### Portée du projet
La portée du projet consiste à l'implémentation des procédures et des exigences du *Code Lespérance* pour le déroulement et propositions d'assemblée déliberante, ainsi que la création de documents connexes aux procédures.

Ce qui n'est pas dans la portée incluent la gestion et présentation des rapports et documentation non-structuré qui peuvent faire parti des instances. Nous n'allons pas non-plus s'occuper des exigences audio-visuelles pour les assemblées.

### Définitions
* Code Lespérance (CL): Un code de procédures pour les assemblées déliberantes
* Procès verbal (PV): Document qui récapitule les procédés d'une assemblée (CL Annexe B.1)

Les propos qui font référence à des règles de procédure seront indiqués avec une note (CL #) avec la règle ou partie du code.

### Assomptions
La grande assomption ici est qu'il y a une structure informatisable créé par l'utilisation de procédures fixes et de l'adaptabilité de cette structure en logiciel. Une divergence entre les attentes du logiciel avec le déroulement de l'assemblée réel pourrait rendre plus difficile et frustrant d'utilisation. Même si pas formalisé, il peut avoir des différences entre les l'application des procédures en théorie par le CL et l'utilisation en practice.

## Besoins des utilisateurs
### Observateurs
* S'ajouter/se retirer à l'ordre de parole
* Faire des interventions prioritaires (point d'ordre/de privilège)
* Voir l'ordre de parole et des points
* Voir les propositions

### Participants
* *Les capacités des observateurs +*
* Faire des propositions
* Créer des (sous-)amendements
* Appuyer des propositions

### Secrétariat
* Ajouter des tours de parole au nom d'autrelui
* Écrire des propositions au nom d'autrelui
* Écrire des sommaires pour les interventions
* Classifier les interventions

### Présidence
* *Les capacités du secrétariat +*
* Accepter des tours de parole
* Accepter des propositions
* Donner/retirer attributs aux participants
* Passer à autres points
* Fermer la scéance
* Modifier les modalités des instances

### Non-participants
* Voir calendrier des instances
* Voir documentation structuré des instances (résolutions/PVs)
* S'inscrire/se connecter pour l'accès

## Solutions
### Gestion d'assemblée
Un utilisateur avec la permission technique approprié peut créer un objet `assemblee` avec un nom, puis y ajouter des `seance`s qui comportent une date et heure de début et fin. Lors de la création de l'objet, des liens sont générés avec du hashage pour qu'autres utilisateurs peuvent s'y joindre avec le rôle attribué avec le lien spécifique pour:
* Membre/Observateur
* Présidence
* Secrétariat

Les liens ne seront pas divulgés ni devinable du à l'hashage. C'est au créateur de l'evenement de faire la distribution. Les séances seront par contre ajouté automatiquement à un calendrier `iCal` publique avec le nom de l'assemblée et détails connexes.

En se connectant à un assemblée par un lien attribué, la personne va saisir son nom ainsi que si elle est votante. Ceci va créer un objet `intervenant` de l'`assemblee` qui peut être attaché à un `utilisateur` du site. Cet objet portera aussi des attributs pour le rôle de l'intervenant comme énumération:
* Observateur
* Membre
* Présidence
* Secrétariat

Les objets auront aussi des attributs propres, soit la capacité à voter ainsi que pour parler.

Avec la création d'assemblée, l'utilisateur aura un objet d'`intervenant` avec le rôle de présidence. Il peut suive avec la création initial de l'ordre du jour. Chaque item de l'ordre du jour est un objet `point` qui inclut la `seance`, le numéro le plus spécifique du point, le point parent (s'il a lieu) et le nom. Pour clarifier avec un exemple, un point "4.3.2" aura le numéro "2" et le point parent le point avec numéro "3" qui lui aurait le "4".

L'existance d'objet `intervenant` serait noté pour prendre les présences.

#### Interface de participant
##### Interface principale
Les participants auront comme page principale un interface avec:
* Bouton pour demander un tour de parole
* Boutons pour point d'ordre ou privilège
* La libellé du point ou proposition actuelle
* Liste des propositions préparées

Pour demander la parole, comme tour ordinaire ou privilegié, sera avec des boutons qui envoie comme message par WebSocket la demande, avec type si spécifié ainsi que la priorité accordée. Le bouton deviens après pour retirer sa demande, qui est traité de la même façon. Quand le tour est pris, un message WebSocket sera reçu pour l'indiquer sur l'interface et reinitialiser le bouton.

Chaque demande crée un objet `intervention` qui prend l'`intervenant` demandeur, le `point` actuel, la `proposition` actuelle, le type d'intervention, la sequence de l'intervention et le tour de parole. Comme types d'intervention, il y a:
* Ordinaire
* D'ordre
* De privilège

La séquence d'intervention est remis à 1 lorsqu'un nouvel ordre de parole est établie, ainsi que le tour (1er tour, 2e tour, etc.). Ces attributs seront nuls jusqu'à la prise de parole, voyant qu'il est impossible de les prédéterminer. La rétraction de demande entraine une suppression de l'objet.

Le bouton pour un tour de parole ordinaire et d'actions relié aux propositions est déactivé si l'`intervenant` n'a pas le droit de parole.

##### Création de proposition
Tout `intervenant` avec droit de parole peut créer des objets `proposition`, qui ont un type associé comme énumération des items dans CL 58, 59, 60, 61 et 62. Ces propositions seront attachés par la suite à un `intervention` quand présenté, soit par la personne durant son temps de parole ou par le secrétariat. L'utilisateur peut aussi indiquer s'il s'agis une position, donc du numéro (0 si pas attribué ou nul si pas une position). Une préambule et la libellé est aussi modifiable.

Les propositions ont un URL unique hashé pour permettre autres participants accès. Autres participants peuvent l'amender, ce qui est avec le même interface, mais avec un champ qui indique la proposition qu'il remplace. Les amendements seront saisies comme un tout, avec la différence entre les versions calculés automatiquement (`diff`).

Autre qu'amender, les participants peuvent appuyer, ce qui associe leur `intervenant` avec la proposition. Après un appuie ou la présentation en `intervention`, le texte n'est plus modifiable et tout modification doit être par nouvelle `proposition`. Le lien pour la proposition est rendu public avec le lien d'un `intervention`.

Si un amendement est adopté pour une proposition, le texte de l'original ne change pas, mais sera dans un nouveau champ. Ceci est important pour pouvoir bien fusionner s'il y a plusieurs amendements sur la même proposition.

##### Vote
Si la proposition ne reçoit pas de débat ou que la présidence ouvre le vote, le bouton pour prendre la parole devient pour demander le vote, ce qui crée un objet `vote` attaché à une proposition et l'`intervenant` le demandant. Les objets ont des attributs pour le nombre de votes pour, contre, abstentions, et si le vote a passé. Les votes par unanimité ne font pas d'objet de vote.

Avec une demande de vote, les trois options sont présentés aux participants éligibles, qui envoie par WebSocket leurs choix ou s'ils se retirent.

Note: Cela fait qu'il n'y a pas vraiment de différence entre les votes secrets et non.

#### Interfaces de présentation
Il y a un couple d'interfaces de lecture (pour présenter):
* Une liste de l'ordre de parole futur
* La proposition en étude

Ce premier indiquerait le point actuel et proposition en haut, puis s'il y a des points privilegiés (et par qui), puis une liste de l'ordre de parole non-épuisé, qui indique (par séparation ou note) leur tour.

La proposition en étude serait un raccourci de la page de proposition en lecture seul, qui inclut la préambule.

#### Interface du secrétariat
La page principale du secrétariat comporte une indication de la `proposition` et `intervention` actuelle, avec un champ pour écrire à propos du discours. Il sera aussi possible de voir les `proposition`s de l'`intervenant` puis les attacher à l'`intervention`, ou d'en créer au nom de l'`intervenant`.

Toute modification aux objets doivent être disponible en temps réel aux autres `intervenant`s du secrétariat, fait avec des `WebSocket`s.

Le secrétairiat peut aussi voir l'ordre des `interventions` passés et de les affecter pareilment.

#### Interface de présidence
La page principale de la présidence comporte le `point` et la `proposition` actuelle avec l'ordre de parole. En selectionnant un nom sur l'ordre, le message `WebSocket` pour l'echange d'`intervention` est envoyé pour mettre à jour les interfaces. Il a aussi un bouton pour indiquer son intervention et pour passer au `vote` de la `proposition` actuelle.

Lorsqu'une `proposition` est achevé, l'ordre de parole précédente incomplète est reprise avec la sequence qui reflète cet ordre-là. La présidence peut choisir de remettre l'ordre à 0 et d'effacer l'ordre future. Il peut donc aussi passer à autres points.

La présidence à aussi une liste des `intervenant`s dans un ordre alphabétique, indiquant s'il y a des duplicats entre noms, pour s'assurer que des délégations n'ont pas plus de votes qu'accordé. Il peut aussi donner et revoquer des droits et types aux `intervenant`s.

Une page pour modifier l'ordre du jour est aussi disponible, comme les `proposition`s portant sur l'ordre du jour ne déclanchent pas des modifications aux `point`s.

La présidence a aussi accès aux capacités du secrétariat, comme pages secondaires.

### Géneration de documentation
La structure des données collectés permettraient à la géneration de certains documents qui découlent de l'assemblée. Ceux-ci incluent:
* l'ordre du jour
* les procès verbaux
* les résolutions
* le cahier de positions

La documentation sera généré en format `HTML`, mais pourrait être adapté pour LaTeX produisant un `PDF` avec une feuille de style fourni.

L'ordre du jour est fait en prenant les `seance`s d'un `assemblee` et de les mettre en liste, avec les `point`s rattachés par parents (si applicable) puis séquence. Les données de l'ordre du jour seront aussi intégré comme calendrier avec `iCal` avec toutes les `assemblee`s.

Le procès verbal est faite en traverçant les `intervention`s avec les résumés ou texte par défaut, et incluant les `proposition`s qui y étaient présentés. Un fil de discussion serait aussi possible, avec les propositions qui comportent sur autres (genre amendements) sur un niveau plus elevé, qui re-descend avec le vote ou l'acclamation.

La liste des résolutions est créé en prenant les `proposition`s ordinaires qui ont passés, les attribuant un code basé sur une acronyme de l'assemblée, le point abordé et l'ordre dans laquelle elles ont été adoptées, dans un format "[x-y-z]" avec hyperlien.

Le cahier de positions serait compilé avec les dernières `proposition`s adoptées avec un tel numéro de position.

### Utilisateurs
Le public serait en capacité de créer des comptes utilisateur unique par personne, qui peut être créé en deux façons, dépendant sur la configuration du site:
1. Formulaire d'inscription public
2. Liens privés uniques envoyés comme invitation pour créer un compte

Un administrateur de site peut accorder des permissions à des utilisateurs, ce qui peuvent être incorporés comme défault avec le formulaire public, ou dans le URL comme configuration de permissions spéciale. Ces permissions seront à l'envergure du site et non pour chaque assemblée.
* Créer des assemblées/séances
* Inviter des utilisateurs aux assemblées
* Voir documentation public
* Voir documentation réstraint
* Se connecter aux assemblées

### Divers

La scission de proposition (CL 76) se ferait comme une seule proposition, mais à son adoption, une proposition ordinaire doit être faite pour chaque partie, chacun qui indique qu'il remplace la même `proposition` originale.
