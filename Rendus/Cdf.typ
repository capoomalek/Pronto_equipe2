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

#outline()

#pagebreak()

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
==== Codes fournis
#table(
  columns: 2,
  [*Fonction*], [franges_objet.py],
  [Objectif], [],
  [Description], [],
  [Contrainte], []
)

#table(
  columns: 2,
  [*Fonction*], [_franges_recepteur.py_],
  [Objectif], [],
  [Description], [],
  [Contrainte], []
)
#table(
  columns: 2,
  [*Fonction*], [_Objet.py_],
  [Objectif], [],
  [Description], [],
  [Contrainte], []
)
#table(
  columns: 2,
  [*Fonction*], [_Trames_binaires.py_],
  [Objectif], [],
  [Description], [],
  [Contrainte], []
)
#table(
  columns: 2,
  [*Fonction*], [_Local_cotes_franges.py_],
  [Objectif], [],
  [Description], [],
  [Contrainte], []
)
#table(
  columns: 2,
  [*Fonction*], [_Local_frange.py_],
  [Objectif], [],
  [Description], [],
  [Contrainte], []
)
#table(
  columns: 2,
  [*Fonction*], [_Damier_emet_recept.py_],
  [Objectif], [],
  [Description], [],
  [Contrainte], []
)

#table(
  columns: 2,
  [*Fonction*], [_Damier_recept.py_],
  [Objectif], [],
  [Description], [],
  [Contrainte], []
)

#table(
  columns: 2,
  [*Fonction*], [_Mire_Damier_],
  [Objectif], [],
  [Description], [],
  [Contrainte], []
)

==== Codes réalisés par l'équipe
#table(
  columns: 2,
  [*Fonction*], [_Toiture.py_],
  [Objectif], [],
  [Description], [],
  [Contrainte], []
)

=== Scénarios
== Validation du besoin
= Le plan de travail
= Organisation

