#import "template.typ": project


#show: project.with(
  title: "Cahier des charges fonctionnel",
  subtitle: "Situation d'apprentissage Physique",
  authors: ("Adrien CONSTANT", "Oscar ESCARMANT", "Malek GHRIBI", "Thomas GUSSE", "Quentin LE PRINCE"),
  date: "03 mars 2026",
  group: "Nantes",          // Mettez votre numéro de groupe,
  logo: "imta_logo.pdf",
  encadrant: "Amanda PORTA"
)

#pagebreak()

test test test

#table(
  columns: 2,
  [*Fonction*], [_Nom de la fonction_],
  [Objectif], [],
  [Description], [],
  [Contrainte], []
)
= Présentation du Projet

== Finalité, mission, objectifs

== Liste des parties prenantes

= Cahier des charges fonctionnel
== Contexte d'utilisation du système
== Expression fonctionnelle du besoin
=== Fonctions de service et de contrainte
=== Scénarios
== Validation du besoin
= Le plan de travail
= Organisation